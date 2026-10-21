/** Scholarship Region discovery -> official-page checks -> review-only drafts.
 * Node 22+, no packages, API keys, or AI calls. Never changes the public hub.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import dns from 'node:dns/promises';
import { isIP } from 'node:net';
import { fileURLToPath } from 'node:url';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SOURCE = 'https://www.scholarshipregion.com';
const AGENT = 'JolsaScholarshipCollector';
const USER_AGENT = `${AGENT}/1.0 (+https://jolsaconsulting.com/contact.html)`;
const BLOCKED = /(^|\.)(scholarshipregion\.com|scholarsregion\.com|facebook\.com|instagram\.com|twitter\.com|x\.com|youtube\.com|youtu\.be|linkedin\.com|t\.me|telegram\.me|whatsapp\.com|wa\.me|google\.com|doubleclick\.net|scholarshipair\.com|opportunitiesforafricans\.com|opportunitydesk\.org|scholars4dev\.com|scholarshipscorner\.website)$/i;

export function decode(text) {
  return text.replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1')
    .replace(/&#(x[0-9a-f]+|\d+);/gi, (_, n) => {
      const code = n[0].toLowerCase() === 'x' ? parseInt(n.slice(1), 16) : Number(n);
      return code > 0 && code <= 0x10ffff ? String.fromCodePoint(code) : '';
    }).replace(/&(amp|lt|gt|quot|apos|nbsp);/g, (_, n) => ({amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:' '})[n]);
}
export function text(html) {
  return decode(html).replace(/<(script|style|nav|footer|header)\b[^>]*>[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
}
export function canonical(raw, base) {
  const u = new URL(decode(raw), base);
  if (u.protocol !== 'https:' || u.username || u.password || (u.port && u.port !== '443')) throw new Error('Only public HTTPS links are supported');
  u.hash = '';
  for (const key of [...u.searchParams.keys()]) if (/^utm_|^(fbclid|gclid)$/i.test(key)) u.searchParams.delete(key);
  return u.href;
}
export function privateAddress(ip) {
  if (isIP(ip) === 6) return !/^2[0-9a-f]{3}:/i.test(ip) && !/^3[0-9a-f]{3}:/i.test(ip);
  const [a,b] = ip.split('.').map(Number);
  return !isIP(ip) || a === 0 || a === 10 || a === 127 || a >= 224 ||
    (a === 169 && b === 254) || (a === 172 && b >= 16 && b <= 31) ||
    (a === 192 && (b === 168 || b === 0)) || (a === 100 && b >= 64 && b <= 127) ||
    (a === 198 && (b === 18 || b === 19));
}

// Apply the most specific user-agent group, then the longest matching rule.
export function robotsRules(body, agent = AGENT) {
  const groups = []; let group = null;
  for (const line of body.split(/\r?\n/)) {
    const match = line.replace(/#.*$/, '').trim().match(/^([\w-]+)\s*:\s*(.*)$/);
    if (!match) continue;
    const [, rawKey, value] = match; const key = rawKey.toLowerCase();
    if (key === 'user-agent') {
      if (!group || group.rules.length) { group = {agents: [], rules: []}; groups.push(group); }
      group.agents.push(value.toLowerCase());
    } else if (group && ['allow','disallow','crawl-delay'].includes(key)) group.rules.push({key,value});
  }
  const score = g => Math.max(-1, ...g.agents.map(a => a === '*' ? 0 : agent.toLowerCase().includes(a) ? a.length : -1));
  const best = Math.max(-1, ...groups.map(score));
  return groups.filter(g => score(g) === best && best >= 0).flatMap(g => g.rules);
}
export function robotsAllowed(rules, url) {
  const u = new URL(url); const target = u.pathname + u.search;
  const matches = rules.filter(r => r.key !== 'crawl-delay' && r.value).filter(r => {
    const pattern = r.value.split('*').map(s => s.replace(/[.+?^${}()|[\]\\]/g, '\\$&')).join('.*').replace(/\\\$$/, '$');
    return new RegExp('^' + pattern).test(target);
  }).sort((a,b) => b.value.replace(/[*$]/g,'').length - a.value.replace(/[*$]/g,'').length || (a.key === 'allow' ? -1 : 1));
  return !matches.length || matches[0].key === 'allow';
}

export class Client {
  constructor() { this.policies = new Map(); this.last = new Map(); }
  async safe(url) {
    const u = new URL(canonical(url));
    const addresses = await dns.lookup(u.hostname, {all:true});
    if (!addresses.length || addresses.some(a => privateAddress(a.address))) throw new Error('Non-public destination refused');
  }
  async request(url, delay = 2000) {
    await this.safe(url);
    const host = new URL(url).host;
    const wait = delay - (Date.now() - (this.last.get(host) || 0));
    if (wait > 0) await new Promise(resolve => setTimeout(resolve, wait));
    this.last.set(host, Date.now());
    const response = await fetch(url, {redirect:'manual', signal:AbortSignal.timeout(25000), headers:{'User-Agent':USER_AGENT, Accept:'text/html,application/rss+xml,application/xml,text/plain'}});
    return response;
  }
  async body(response) {
    let size = 0; const chunks = [];
    for await (const chunk of response.body) {
      size += chunk.length;
      if (size > 3_000_000) { await response.body.cancel().catch(() => {}); throw new Error('Page exceeds 3 MB limit'); }
      chunks.push(chunk);
    }
    return Buffer.concat(chunks).toString('utf8');
  }
  async policy(url) {
    const origin = new URL(url).origin;
    if (this.policies.has(origin)) return this.policies.get(origin);
    let robotsUrl = origin + '/robots.txt'; let response;
    for (let redirects = 0; redirects <= 5; redirects++) {
      response = await this.request(robotsUrl);
      if (![301,302,303,307,308].includes(response.status)) break;
      const next = canonical(response.headers.get('location'),robotsUrl);
      await response.body?.cancel(); robotsUrl = next;
    }
    let rules;
    if (response.status === 404 || response.status === 410) rules = [];
    else if (response.ok && !(response.headers.get('content-type') || '').includes('text/html')) rules = robotsRules(await this.body(response));
    else throw new Error(`Cannot establish robots.txt permission (HTTP ${response.status})`);
    this.policies.set(origin, rules); return rules;
  }
  async get(raw, discovery = false) {
    let url = canonical(raw);
    for (let redirects = 0; redirects <= 5; redirects++) {
      if (discovery && new URL(url).hostname !== 'www.scholarshipregion.com' && new URL(url).hostname !== 'scholarshipregion.com') throw new Error('Discovery must stay on Scholarship Region');
      const rules = await this.policy(url);
      if (!robotsAllowed(rules, url)) throw new Error('Access disallowed by robots.txt');
      const delay = Math.max(2000, ...rules.filter(r => r.key === 'crawl-delay').map(r => Number(r.value) * 1000 || 0));
      if (delay > 30000) throw new Error('Source requests a crawl delay above this job’s limit');
      const response = await this.request(url, delay);
      if ([301,302,303,307,308].includes(response.status)) { url = canonical(response.headers.get('location'), url); await response.body?.cancel(); continue; }
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      if (!/text\/html|application\/(rss\+xml|xml)|text\/(xml|plain)/i.test(response.headers.get('content-type') || '')) throw new Error('Unsupported page type (PDFs need manual review)');
      return {url, html:await this.body(response)};
    }
    throw new Error('Too many redirects');
  }
}

export function parseFeed(xml) {
  if (!/<rss\b/i.test(xml)) throw new Error('Scholarship Region did not return an RSS feed');
  const items = [...xml.matchAll(/<item\b[^>]*>([\s\S]*?)<\/item>/gi)].map(([, item]) => {
    const tag = name => text(item.match(new RegExp(`<${name}[^>]*>([\\s\\S]*?)<\\/${name}>`, 'i'))?.[1] || '');
    return {title:tag('title'), url:tag('link'), categories:[...item.matchAll(/<category[^>]*>([\s\S]*?)<\/category>/gi)].map(m => text(m[1])), published:tag('pubDate')};
  });
  return items.filter(i => /scholarship|fellowship/i.test(i.title) && i.categories.some(c => /scholarship|fellowship/i.test(c)) && !/^(top\b|\d{1,2}\s)|universities (offering|that)|how to|success stor/i.test(i.title));
}
export function officialLinks(html, base, allowIntermediary = false) {
  const content = (html.match(/<article\b[^>]*>([\s\S]*?)<\/article>/i)?.[1] || html)
    .replace(/<(script|style|nav|footer|header)\b[^>]*>[\s\S]*?<\/\1>/gi, ' ');
  const links = [];
  for (const match of content.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/gi)) {
    const raw = match[1].match(/\bhref\s*=\s*["']([^"']+)["']/i)?.[1]; if (!raw) continue;
    try {
      const url = canonical(raw, base); const label = text(match[2]); const u = new URL(url);
      const intermediary = allowIntermediary && /^(www\.)?scholarsregion\.com$/.test(u.hostname) && u.pathname.startsWith('/scholarship/');
      if ((!intermediary && BLOCKED.test(u.hostname)) || /\.(png|jpg|jpeg|gif|webp|svg)$/i.test(u.pathname)) continue;
      const score = /apply|official|visit.*(website|page)|application.*(link|portal)|click here/i.test(label) ? 10 : /\.edu(\.|$)|\.ac\.|\.gov(\.|$)/i.test(u.hostname) ? 3 : 0;
      if (score) links.push({url, label, score});
    } catch { /* Non-HTTPS and malformed links are not sources. */ }
  }
  return [...new Map(links.sort((a,b) => b.score-a.score).map(l => [l.url,l])).values()].slice(0,3);
}

// Scholarship Region now routes many application buttons through its new
// ScholarsRegion pages. Read their server-rendered data as data, never execute JS.
export function intermediaryLinks(html, base) {
  let payload = '';
  for (const match of html.matchAll(/self\.__next_f\.push\((\[[\s\S]*?\])\)\s*;?/g)) {
    try { const value = JSON.parse(match[1]); if (value[0] === 1 && typeof value[1] === 'string') payload += value[1]; } catch { /* Unknown hydration shape: leave for manual review. */ }
  }
  const raw = payload.match(/"externalLink"\s*:\s*"([^"\s]+)"/)?.[1];
  const links = [];
  if (raw) {
    try {
      const url = canonical(raw.replace(/\\\//g,'/'),base);
      if (!BLOCKED.test(new URL(url).hostname)) links.push({url,label:'Provider application link',score:20});
    } catch { /* Invalid embedded link. */ }
  }
  // Also inspect visible links, and scholarship body links on the same provider
  // domain as the primary application link (useful when that link is a PDF).
  links.push(...officialLinks(html,base));
  if (links[0]) {
    const providerHost = new URL(links[0].url).hostname.replace(/^www\./,'');
    const decoded = payload.replace(/\\"/g,'"').replace(/\\u003c/gi,'<').replace(/\\u003e/gi,'>');
    for (const match of decoded.matchAll(/href="(https:[^"]+)"/g)) {
      try {
        const url = canonical(match[1],base); const host = new URL(url).hostname.replace(/^www\./,'');
        if (host === providerHost || host.endsWith('.'+providerHost)) links.push({url,label:'Provider information page',score:15});
      } catch { /* Malformed source link. */ }
    }
  }
  return [...new Map(links.map(l => [l.url,l])).values()].slice(0,3);
}

// Only short evidence hints: dates are candidates, never asserted as deadlines.
export function inspectOfficial(html) {
  const title = text(html.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/i)?.[1] || html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] || '');
  const plain = text(html);
  const dates = [...new Set(plain.match(/\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b/gi) || [])].slice(0,12);
  return {page_title:title.slice(0,240), date_candidates:dates, mentions_scholarship:/scholarship|fellowship|funding|financial aid/i.test(plain)};
}
export function slugify(title) { return text(title).toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,110); }
const md = value => String(value).replace(/[\r\n]/g,' ').replace(/[<>\[\]`*_]/g,'');
export function draftMarkdown(draft) {
  return `# Scholarship opportunity: ${md(draft.discovery_title)}\n\nStatus: needs human review; not published.\n\nDiscovered on [Scholarship Region](${draft.discovery_url}).\nChecked: ${draft.checked_at}\n\n## Official-source candidates\n\n${draft.sources.map(s => `- [${md(s.page_title || s.label || 'Candidate source')}](${s.url}) — ${s.error ? md(s.error) : 'page retrieved; provider identity and application cycle need confirmation'}\n  Date mentions (not confirmed deadlines): ${(s.date_candidates || []).map(md).join(', ') || 'none extracted'}`).join('\n') || '- No official-source candidate found; research manually.'}\n\n## Proposed listing\n\nThis opportunity was discovered through Scholarship Region. Before applying, confirm the programme, current application cycle, eligibility, funding, and deadline on the provider’s official website.\n\n## Required review\n\n- Confirm that the selected source belongs to the scholarship provider.\n- Confirm that applications are open or will open within 60 days.\n- Fill in the companion JSON from official sources: title, level, country, funding_type, deadline, status, summary, meta_description, funder, official_url, body_html.\n- Write original explanatory text; do not copy the discovery article.\n- Set reviewed to true only after checking every field.\n- Promote with: python scripts/publish_scholarship_draft.py automation/drafts/${draft.id}.json\n\nNo eligibility, funding amount, or deadline has been inferred from the discovery article.\n`;
}

export async function collect({root=ROOT, client=new Client(), now=new Date(), maxArticles=20, batchSize=5, dryRun=false} = {}) {
  const checked = now.toISOString().slice(0,10);
  const data = JSON.parse(await fs.readFile(path.join(root,'scholarships.json'),'utf8'));
  const draftDir = path.join(root,'automation','drafts');
  const existing = new Set(data.scholarships.flatMap(s => [s.discovery_url, s.official_url, ...(s.sources_cited || [])]).filter(Boolean));
  const names = await fs.readdir(draftDir).catch(e => e.code === 'ENOENT' ? [] : Promise.reject(e));
  for (const name of names.filter(n => n.endsWith('.json'))) {
    const d = JSON.parse(await fs.readFile(path.join(draftDir,name),'utf8')); existing.add(d.discovery_url);
  }
  const report = {checked_at:checked, discovery_source:SOURCE, scanned:0, drafts:[], skipped:[], errors:[]};
  let feed;
  try { feed = parseFeed((await client.get(SOURCE + '/feed/',true)).html); }
  catch (e) { report.errors.push({url:SOURCE+'/feed/',reason:e.message}); }
  if (feed && !feed.length) report.errors.push({url:SOURCE+'/feed/',reason:'No scholarship items found; feed layout or category names may have changed'});
  for (const item of (feed || []).slice(0,maxArticles)) {
    if (report.drafts.length >= batchSize) break;
    let discoveryUrl;
    try { discoveryUrl = canonical(item.url); } catch { continue; }
    if (existing.has(discoveryUrl)) { report.skipped.push({url:discoveryUrl,reason:'Already collected'}); continue; }
    report.scanned++;
    try {
      const article = await client.get(discoveryUrl,true);
      const discovered = officialLinks(article.html,article.url,true);
      const candidates = [];
      for (const link of discovered) {
        if (/^(www\.)?scholarsregion\.com$/.test(new URL(link.url).hostname)) {
          try {
            const intermediate = await client.get(link.url);
            if (!/^(www\.)?scholarsregion\.com$/.test(new URL(intermediate.url).hostname)) throw new Error('Unexpected intermediary redirect');
            const onward = intermediaryLinks(intermediate.html,intermediate.url);
            if (!onward.length) report.errors.push({url:link.url,reason:'Intermediary has no provider link; research manually'});
            candidates.push(...onward.map(l => ({...l,via:intermediate.url})));
          } catch(e) { report.errors.push({url:link.url,reason:e.message}); }
        } else candidates.push(link);
      }
      const sources = [];
      for (const candidate of candidates.slice(0,3)) {
        if (existing.has(candidate.url)) continue;
        try {
          const official = await client.get(candidate.url);
          if (BLOCKED.test(new URL(official.url).hostname)) throw new Error('Redirect points to a discovery or social site');
          if (existing.has(official.url)) continue;
          sources.push({...candidate,url:official.url,...inspectOfficial(official.html)});
        } catch(e) { sources.push({...candidate,error:e.message}); }
      }
      if (!sources.length) { report.skipped.push({url:discoveryUrl,reason:candidates.length ? 'Official sources already collected' : 'No official application/source link found'}); continue; }
      if (!sources.some(s => !s.error && s.mentions_scholarship)) { report.errors.push({url:discoveryUrl,reason:'No readable scholarship source; requires manual research',sources}); continue; }
      const id = slugify(item.title);
      if (!id || names.includes(id+'.json')) { report.skipped.push({url:discoveryUrl,reason:'Duplicate draft title'}); continue; }
      const draft = {id,discovery_title:item.title,discovery_url:discoveryUrl,checked_at:checked,reviewed:false,sources,
        listing:{title:null,level:[],country:null,funding_type:null,deadline:null,status:null,summary:null,meta_description:null,funder:null,official_url:null,body_html:null}};
      if (!dryRun) {
        await fs.mkdir(draftDir,{recursive:true});
        await fs.writeFile(path.join(draftDir,id+'.json'),JSON.stringify(draft,null,2)+'\n');
        await fs.writeFile(path.join(draftDir,id+'.md'),draftMarkdown(draft));
      }
      names.push(id+'.json'); existing.add(discoveryUrl);
      for (const s of sources.filter(s => !s.error)) existing.add(s.url);
      report.drafts.push({id,title:item.title,discovery_url:discoveryUrl});
    } catch(e) { report.errors.push({url:discoveryUrl,reason:e.message}); }
  }
  const markdown = `# Weekly scholarship collection — ${checked}\n\nDiscovery source: Scholarship Region only. No paid AI service used.\n\nArticles checked: ${report.scanned}. New review drafts: ${report.drafts.length}. Errors: ${report.errors.length}.\n\n## Drafts\n\n${report.drafts.map(d => `- [${md(d.title)}](drafts/${d.id}.md)`).join('\n') || 'No new drafts.'}\n\n## Skipped\n\n${report.skipped.map(s => `- ${s.url}: ${md(s.reason)}`).join('\n') || 'None.'}\n\n## Source failures\n\n${report.errors.map(s => `- ${s.url}: ${md(s.reason)}${(s.sources || []).map(p => `\n  - ${p.url}: ${md(p.error || 'No scholarship information identified')}`).join('')}`).join('\n') || 'None.'}\n\nDrafts require review and promotion before they appear on the scholarship hub.\n`;
  if (!dryRun) {
    await fs.mkdir(path.join(root,'automation'),{recursive:true});
    await fs.writeFile(path.join(root,'automation','latest-report.json'),JSON.stringify(report,null,2)+'\n');
    await fs.writeFile(path.join(root,'automation','latest-report.md'),markdown);
  }
  return {report,markdown,failed:!!report.errors.length && !report.drafts.length};
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const bounded = (name,fallback,max) => { const n = Number(process.env[name] || fallback); if (!Number.isInteger(n) || n < 1 || n > max) throw new Error(`${name} must be between 1 and ${max}`); return n; };
  try {
    const result = await collect({dryRun:process.argv.includes('--dry-run'),batchSize:bounded('SCHOLARSHIP_POST_BATCH_SIZE',5,10),maxArticles:bounded('SCHOLARSHIP_MAX_ARTICLES',20,40)});
    console.log(result.markdown);
    if (process.env.GITHUB_STEP_SUMMARY) await fs.appendFile(process.env.GITHUB_STEP_SUMMARY,result.markdown);
    if (process.env.GITHUB_OUTPUT) await fs.appendFile(process.env.GITHUB_OUTPUT,`count=${result.report.drafts.length}\n`);
    if (result.failed) process.exitCode = 1;
  } catch(e) { console.error(`Collector failed: ${e.message}`); process.exitCode = 1; }
}
