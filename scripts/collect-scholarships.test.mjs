import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {Client,parseFeed,officialLinks,intermediaryLinks,inspectOfficial,collect,robotsRules,robotsAllowed,canonical,privateAddress} from './collect-scholarships.mjs';

const article = 'https://www.scholarshipregion.com/example-award/';
const official = 'https://university.edu/funding/award';
const feed = `<rss><channel><item><title><![CDATA[2027 Example Scholarship &amp; Award]]></title><link>${article}</link><category><![CDATA[Masters Scholarships]]></category></item><item><title>Top 10 Scholarships</title><link>https://www.scholarshipregion.com/top/</link><category>Scholarships</category></item><item><title>Student wins scholarship</title><category>Success Stories</category></item></channel></rss>`;

test('RSS discovery handles CDATA/entities and excludes roundups and success stories', () => {
  assert.deepEqual(parseFeed(feed).map(i => i.title), ['2027 Example Scholarship & Award']);
  assert.throws(() => parseFeed('<html>Access denied</html>'), /RSS/);
});
test('application links exclude social, discovery, and insecure destinations', () => {
  const links = officialLinks(`<article><a href="https://wa.me/123">Apply now</a><a href="/other/">Apply now</a><a href="http://unsafe.edu/">Official website</a><a href="${official}?utm_source=sr">Visit official website</a></article>`,article);
  assert.equal(links.length,1); assert.equal(links[0].url,official);
});
test('official inspection labels date mentions without inventing deadlines', () => {
  const result = inspectOfficial('<title>Example award</title><main>Scholarship opens 21 October 2026. Deadline: 2027-01-31.</main>');
  assert.deepEqual(result.date_candidates,['21 October 2026','2027-01-31']);
  assert.equal(result.deadline,undefined);
});
test('Scholarship Region intermediary is followed to the provider, never treated as official', async t => {
  const middle = 'https://scholarsregion.com/scholarship/example-award';
  assert.equal(officialLinks(`<a href="${middle}">Apply now</a>`,article).length,0);
  const payload = JSON.stringify([1, `32:{"externalLink":"${official}"}`]);
  const html = `<script>self.__next_f.push(${payload})</script>`;
  assert.equal(intermediaryLinks(html,middle)[0].url,official);
  const root = await workspace(t);
  const client = {async get(url) {
    if (url === article) return {url,html:`<article><a href="${middle}">Apply now</a></article>`};
    if (url === middle) return {url,html};
    return mock.get(url);
  }};
  const result = await collect({root,client});
  assert.equal(result.report.drafts.length,1);
  const d = JSON.parse(await fs.readFile(path.join(root,'automation','drafts',result.report.drafts[0].id+'.json'),'utf8'));
  assert.equal(d.sources[0].url,official); assert.equal(d.sources[0].via,middle);
});
test('robots uses longest rule, named agents, wildcards, and query strings', () => {
  const rules = robotsRules('User-agent: *\nDisallow: /private/\nAllow: /private/public/\nDisallow: /*?secret=*\n');
  assert.equal(robotsAllowed(rules,'https://site.edu/private/x'),false);
  assert.equal(robotsAllowed(rules,'https://site.edu/private/public/x'),true);
  assert.equal(robotsAllowed(rules,'https://site.edu/?secret=1'),false);
  assert.equal(robotsAllowed(robotsRules('User-agent: *\nAllow: /\nUser-agent: JolsaScholarshipCollector\nDisallow: /'),'https://site.edu/'),false);
});
test('URL safety rejects local/private destinations and non-HTTPS links', () => {
  for (const ip of ['127.0.0.1','10.0.0.1','172.16.0.1','192.168.1.1','169.254.169.254','::1','::ffff:127.0.0.1','fd00::1']) assert.equal(privateAddress(ip),true,ip);
  assert.equal(privateAddress('8.8.8.8'),false);
  assert.throws(() => canonical('http://example.edu/'));
  assert.throws(() => canonical('https://user:pass@example.edu/'));
});
test('robots redirects are followed, cached, and applied before page access', async () => {
  const client = new Client(); const calls = [];
  client.request = async url => {
    calls.push(url);
    if (url === 'https://provider.edu/robots.txt') return new Response('',{status:301,headers:{location:'https://www.provider.edu/robots.txt'}});
    return new Response('User-agent: *\nDisallow: /private/',{headers:{'content-type':'text/plain'}});
  };
  const rules = await client.policy('https://provider.edu/scholarship');
  assert.equal(robotsAllowed(rules,'https://provider.edu/private/'),false);
  await client.policy('https://provider.edu/other'); assert.equal(calls.length,2);
});

async function workspace(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(),'jolsa-collector-'));
  t.after(() => fs.rm(root,{recursive:true,force:true}));
  await fs.writeFile(path.join(root,'scholarships.json'),'{"scholarships":[]}');
  return root;
}
const mock = {async get(url) {
  if (url.endsWith('/feed/')) return {url,html:feed};
  if (url === article) return {url,html:`<article><a href="${official}">Official website</a></article>`};
  if (url === official) return {url,html:'<h1>Example scholarship</h1><p>Applications close 31 January 2027.</p>'};
  throw new Error('Unexpected request '+url);
}};
test('end-to-end collection writes review drafts, preserves public listings, and deduplicates reruns', async t => {
  const root = await workspace(t); const original = await fs.readFile(path.join(root,'scholarships.json'),'utf8');
  const options = {root,client:mock,now:new Date('2026-10-21T12:00:00Z')};
  const first = await collect(options); assert.equal(first.report.drafts.length,1); assert.equal(first.failed,false);
  const id = first.report.drafts[0].id;
  const draft = JSON.parse(await fs.readFile(path.join(root,'automation','drafts',id+'.json'),'utf8'));
  assert.equal(draft.reviewed,false); assert.equal(draft.listing.deadline,null); assert.equal(draft.sources[0].url,official);
  assert.equal(await fs.readFile(path.join(root,'scholarships.json'),'utf8'),original);
  assert.equal((await collect(options)).report.drafts.length,0);
});
test('dry run performs discovery without creating files', async t => {
  const root = await workspace(t); const result = await collect({root,client:mock,dryRun:true});
  assert.equal(result.report.drafts.length,1);
  await assert.rejects(fs.access(path.join(root,'automation')));
});
test('blocked official source fails visibly and never creates a misleading draft', async t => {
  const root = await workspace(t);
  const client = {async get(url) { if (url === official) throw new Error('Access disallowed by robots.txt'); return mock.get(url); }};
  const result = await collect({root,client}); assert.equal(result.failed,true); assert.equal(result.report.drafts.length,0);
  assert.match(JSON.stringify(result.report.errors),/robots/);
});
test('feed failure is reported and does not masquerade as an empty successful run', async t => {
  const root = await workspace(t);
  const result = await collect({root,client:{async get() { throw new Error('HTTP 403'); }}});
  assert.equal(result.failed,true); assert.match(result.markdown,/HTTP 403/);
});
