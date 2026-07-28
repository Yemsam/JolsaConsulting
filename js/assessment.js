(() => {
  "use strict";

  const standard = [
    { label: "Yes, completely", score: 3 },
    { label: "Partly", score: 2 },
    { label: "I am not sure", score: 1 },
    { label: "Not yet", score: 0 },
  ];

  const sections = [
    { id: "academic", title: "Academic Profile", description: "Your education, performance, progression, and connection to future study.", questions: [
      { id: "qualification", text: "What is your highest completed qualification?", options: [{label:"Postgraduate degree",score:3},{label:"Bachelor's degree or HND",score:3},{label:"Diploma or equivalent",score:2},{label:"Secondary school qualification",score:1}] },
      { id: "performance", text: "How would you describe your academic performance?", options: [{label:"Strong and competitive",score:3},{label:"Generally good",score:2},{label:"Mixed or difficult to explain",score:1},{label:"Below most entry requirements",score:0}] },
      { id: "education_relevance", text: "Is your proposed course connected to your previous education?", options: standard },
      { id: "gap", text: "Can you clearly explain any academic or career gaps and your progression?", options: standard },
    ]},
    { id: "career", title: "Career and Experience", description: "Your practical experience, achievements, progression, and wider contribution.", questions: [
      { id: "experience", text: "Do you have professional or practical experience?", options: standard },
      { id: "experience_relevance", text: "Is your experience relevant to your proposed course or career direction?", options: standard },
      { id: "achievements", text: "Can you demonstrate measurable achievements or meaningful impact?", options: standard },
      { id: "leadership", text: "Do you have leadership, volunteer, research, or community experience?", options: standard },
    ]},
    { id: "strategy", title: "Course and Country Strategy", description: "How clearly you have defined and researched a suitable study direction.", questions: [
      { id: "course_selected", text: "Have you selected a specific course or academic field?", options: standard },
      { id: "career_connection", text: "Can you explain how the course supports your career goals?", options: standard },
      { id: "university_research", text: "Have you researched universities offering the course?", options: standard },
      { id: "requirements_compared", text: "Have you compared requirements and considered more than one suitable destination?", options: standard },
    ]},
    { id: "funding", title: "Funding and Scholarship Readiness", description: "Your understanding of costs, funding options, and scholarship positioning.", questions: [
      { id: "cost_awareness", text: "Do you know the approximate tuition and living costs for your destination?", options: standard },
      { id: "funding_plan", text: "Do you have a realistic funding plan?", options: [{label:"Yes, with confirmed or realistic sources",score:3},{label:"Partly; some funding is still unclear",score:2},{label:"I am relying entirely on scholarships",score:1,flag:"scholarship_only"},{label:"Not yet",score:0}] },
      { id: "scholarship_research", text: "Have you researched suitable scholarships and their deadlines?", options: standard },
      { id: "scholarship_evidence", text: "Can you evidence achievements and explain why you deserve scholarship support?", options: standard },
    ]},
    { id: "documents", title: "Application Documents", description: "The readiness, relevance, and consistency of your application materials.", questions: [
      { id: "cv", text: "Do you have an updated CV tailored to your study objective?", options: standard },
      { id: "sop", text: "Have you prepared a statement of purpose or personal statement?", options: standard },
      { id: "references", text: "Can you obtain strong recommendation letters?", options: standard },
      { id: "records", text: "Are your transcripts and certificates available, with details consistent across your documents?", options: standard },
    ]},
    { id: "timeline", title: "Timeline and Visa Readiness", description: "Your deadlines, travel documents, financial preparation, and visa understanding.", questions: [
      { id: "timeline_plan", text: "Is your planned study start at least 6–12 months away, or are you already well prepared for a nearer intake?", options: standard },
      { id: "passport_deadlines", text: "Do you have a valid passport and know your institution deadlines?", options: standard },
      { id: "financial_documents", text: "Have you started planning the financial documents that may be required?", options: standard },
      { id: "visa_knowledge", text: "Do you understand the general visa process and feel ready to explain your study purpose and future plans?", options: standard },
    ]},
  ];

  const feedback = {
    academic: { strength:"Your academic background provides a useful base for demonstrating readiness and progression.", low:"Your academic story may need clearer evidence or explanation. Check entry requirements and prepare a concise account of your progression and any gaps.", actions:["Compare your qualifications and grades with the published entry requirements for each target course.","Prepare a clear explanation of how your education and any gaps support your next academic step."] },
    career: { strength:"Your experience and contributions can help you show practical value beyond grades alone.", low:"Your experience or achievements may not yet be clearly evidenced. Identify relevant responsibilities, results, leadership, research, or community contribution.", actions:["Write down three relevant achievements using specific outcomes, evidence, or measurable impact.","Connect your work, volunteering, research, or leadership experience to the skills your proposed course requires."] },
    strategy: { strength:"You have a defined study direction and can make more focused course and destination choices.", low:"Your course and destination choices need a stronger evidence-based strategy. Clear academic and career fit reduces unsuitable applications.", actions:["Clarify the field and qualification you want to pursue before choosing a country or university.","Build a shortlist of at least five universities and compare eligibility, tuition, funding, location, career relevance, and deadlines."] },
    funding: { strength:"Your cost awareness and funding preparation give you a more realistic application foundation.", low:"Your cost or scholarship plan may have important gaps. Funding affects course choice, application timing, and visa preparation.", actions:["Estimate tuition, accommodation, living expenses, travel, insurance, and visa-related costs for each destination.","Research scholarships early and keep an alternative funding plan because awards are competitive."] },
    documents: { strength:"Your core documents are taking shape and can support a consistent, persuasive application story.", low:"Missing or generic documents could weaken how your profile is understood. Strong materials should be relevant, specific, and consistent.", actions:["Create a study-focused CV highlighting relevant education, achievements, leadership, research, volunteering, and transferable skills.","Gather transcripts, certificates, and recommenders, then outline your motivation, relevant experience, course choice, and career direction for your statement."] },
    timeline: { strength:"Your timeline and visa awareness should help you avoid preventable deadline and preparation problems.", low:"Your schedule or visa preparation may be too early-stage. Deadlines and official requirements can determine whether your plan is workable.", actions:["Create a calendar for university, scholarship, document, and visa milestones, allowing time for delays.","Review current student-visa requirements only through the relevant official immigration authority."] },
  };

  const levels = [
    [39,"Foundation Stage","You are still at an early stage of your study-abroad preparation. This does not mean that studying abroad is impossible. Strengthen your direction, planning, documents, and funding strategy before submitting applications."],
    [59,"Developing Profile","You already have some useful elements in place, but important gaps could weaken your application. Develop a clearer strategy and improve the weakest parts of your profile."],
    [74,"Promising but Needs Improvement","Your profile shows good potential, but some areas still need focused improvement. Stronger program selection and better-prepared documents could significantly improve your position."],
    [89,"Strong Preparation","You appear to have a strong preparation base. Ensure your course choices, documents, funding strategy, and overall story are competitive and consistent."],
    [100,"Advanced Readiness","You appear well prepared in many important areas. Because every process has specific requirements, a final strategic review may help you avoid preventable mistakes."],
  ];

  let current = 0;
  const answers = {};
  const form = document.querySelector("#assessment-form");
  if (!form) return;
  const container = document.querySelector("#question-container");
  const validation = document.querySelector("#validation-message");
  const previous = document.querySelector("#previous-button");
  const next = document.querySelector("#next-button");

  const escapeHtml = (value) => { const el=document.createElement("div"); el.textContent=value; return el.innerHTML; };
  const pct = (points, count) => Math.round((points / (count * 3)) * 100);

  function renderSection() {
    const section = sections[current];
    container.innerHTML = `<fieldset class="question-section"><legend>${escapeHtml(section.title)}</legend><p class="section-description">${escapeHtml(section.description)}</p>${section.questions.map((q,i)=>`<article class="question-card" data-question="${q.id}"><h3>${i+1}. ${escapeHtml(q.text)} <span class="required-mark" aria-hidden="true">*</span><span class="sr-only">required</span></h3><div class="answer-options">${q.options.map((o,j)=>`<label class="answer-option"><input type="radio" name="${q.id}" value="${j}" ${answers[q.id]?.index===j?"checked":""} required /><span>${escapeHtml(o.label)}</span></label>`).join("")}</div></article>`).join("")}</fieldset>`;
    container.querySelectorAll("input").forEach(input=>input.addEventListener("change",(e)=>{const q=section.questions.find(item=>item.id===e.target.name); const index=Number(e.target.value); answers[q.id]={index,score:q.options[index].score,flag:q.options[index].flag||""}; e.target.closest(".question-card").classList.remove("invalid"); validation.textContent="";}));
    const step=current+1; document.querySelector("#progress-label").textContent=`Section ${step} of ${sections.length} — ${section.title}`; document.querySelector("#progress-percent").textContent=`${Math.round(step/sections.length*100)}% complete`; document.querySelector("#progress-bar").style.width=`${step/sections.length*100}%`;
    previous.hidden=current===0; next.textContent=current===sections.length-1?"View My Results":"Continue"; validation.textContent="";
  }

  function validateSection() {
    const missing=sections[current].questions.filter(q=>!answers[q.id]);
    container.querySelectorAll(".question-card").forEach(card=>card.classList.toggle("invalid",missing.some(q=>q.id===card.dataset.question)));
    if(missing.length){validation.textContent=`Please answer ${missing.length===1?"the highlighted question":`all ${missing.length} highlighted questions`} before continuing.`; container.querySelector(".question-card.invalid input").focus(); return false;} return true;
  }

  function getScores() { return sections.map(section=>{const points=section.questions.reduce((sum,q)=>sum+answers[q.id].score,0); return {...section,points,percentage:pct(points,section.questions.length)};}); }

  function getActions(scores) {
    const actions=[]; const add=(text)=>{if(!actions.includes(text))actions.push(text);};
    const critical={course_selected:"Clarify the field and qualification you want to pursue before selecting a destination or university.",university_research:"Build a shortlist based on eligibility, tuition, funding, location, career relevance, and deadlines.",cv:"Create a study-focused CV that highlights relevant achievements, not only responsibilities.",funding_plan:"Estimate the full cost of tuition, accommodation, living expenses, travel, insurance, and visa requirements.",sop:"Define your motivation, relevant experience, career direction, reasons for the program, and expected value before drafting your statement.",financial_documents:"Start identifying the financial evidence required and allow enough time to prepare it."};
    Object.entries(critical).forEach(([id,text])=>{if(answers[id]?.score<=1)add(text);});
    if(answers.funding_plan?.flag==="scholarship_only") add("Develop both a scholarship strategy and an alternative funding plan; scholarships are competitive and not guaranteed.");
    scores.slice().sort((a,b)=>a.percentage-b.percentage).forEach(s=>feedback[s.id].actions.forEach(add));
    if(answers.timeline_plan?.score<=1 && scores.reduce((n,s)=>n+s.percentage,0)/scores.length<60) add("Your intended timeline may be too close for your current preparation. Review deadlines now and consider whether a later intake would support a stronger application.");
    return actions.slice(0,5);
  }

  function getService(scores,overall) {
    const weak=scores.filter(s=>s.percentage<60); const lowest=scores.slice().sort((a,b)=>a.percentage-b.percentage)[0];
    if(overall>=75) return ["Final Application Strategy Review","You have a promising preparation base. A final strategic review can help identify hidden weaknesses and ensure your documents and choices are consistent before submission."];
    if(weak.length>=3) return ["Comprehensive Application Support","Your answers show that you may benefit from support across several stages, including profile strategy, university selection, documents, funding preparation, and application planning."];
    if(lowest.id==="strategy") return ["Study-Abroad Strategy Consultation","Your greatest need appears to be strategic direction. A consultation can help clarify suitable courses, destinations, priorities, and next steps."];
    if(lowest.id==="documents") return ["CV and Application Document Review","Your strengths may not yet be presented effectively. A professional review can improve the relevance, consistency, structure, and positioning of your documents."];
    if(lowest.id==="funding") return ["Scholarship Strategy Support","You may benefit from identifying suitable scholarships and strengthening the evidence, positioning, and written materials needed for competitive applications."];
    return ["Comprehensive Application Support","Focused support can help you strengthen your weakest preparation area while keeping your strategy, documents, funding, and timeline consistent."];
  }

  function showResults() {
    const scores=getScores(); const total=scores.reduce((sum,s)=>sum+s.points,0); const max=sections.reduce((sum,s)=>sum+s.questions.length*3,0); const overall=Math.round(total/max*100); const level=levels.find(l=>overall<=l[0]);
    const ranked=scores.slice().sort((a,b)=>b.percentage-a.percentage); const name=document.querySelector("#first-name").value.trim();
    document.querySelector("#result-title").textContent=name?`${name}, Your Study-Abroad Readiness Result`:"Your Study-Abroad Readiness Result";
    document.querySelector("#result-summary").textContent=`Overall Readiness Score: ${overall}%`; document.querySelector("#overall-score").textContent=`${overall}%`; document.querySelector("#score-ring").style.background=`conic-gradient(var(--gold) ${overall}%, #e8e6e1 ${overall}%)`; document.querySelector("#readiness-level").textContent=level[1]; document.querySelector("#readiness-message").textContent=level[2];
    document.querySelector("#category-breakdown").innerHTML=scores.map(s=>`<div class="category-row"><strong>${escapeHtml(s.title)}</strong><div class="category-bar" aria-label="${escapeHtml(s.title)}: ${s.percentage}%"><span style="width:${s.percentage}%"></span></div><strong>${s.percentage}%</strong></div>`).join("");
    document.querySelector("#strengths").innerHTML=ranked.slice(0,2).map(s=>`<div class="feedback-card"><strong>${escapeHtml(s.title)} — ${s.percentage}%</strong><p>${feedback[s.id].strength}</p></div>`).join("");
    document.querySelector("#priorities").innerHTML=ranked.slice(-3).reverse().map(s=>`<div class="feedback-card"><strong>${escapeHtml(s.title)} — ${s.percentage}%</strong><p>${feedback[s.id].low}</p></div>`).join("");
    document.querySelector("#action-plan").innerHTML=getActions(scores).map(a=>`<li>${escapeHtml(a)}</li>`).join(""); const service=getService(scores,overall); document.querySelector("#service-name").textContent=service[0]; document.querySelector("#service-copy").textContent=service[1];
    document.querySelector("#questionnaire").hidden=true; document.querySelector("#results").hidden=false; document.querySelector("#results").scrollIntoView({behavior:"smooth",block:"start"});
  }

  previous.addEventListener("click",()=>{if(current>0){current--;renderSection(); document.querySelector("#assessment").scrollIntoView({behavior:"smooth"});}});
  next.addEventListener("click",()=>{if(!validateSection())return; if(current<sections.length-1){current++;renderSection(); document.querySelector("#assessment").scrollIntoView({behavior:"smooth"});}else showResults();});
  document.querySelector("#print-button").addEventListener("click",()=>window.print());
  document.querySelector("#retake-button").addEventListener("click",()=>{Object.keys(answers).forEach(k=>delete answers[k]); current=0; form.reset(); document.querySelector("#first-name").value=""; document.querySelector("#results").hidden=true; document.querySelector("#questionnaire").hidden=false; renderSection(); document.querySelector("#assessment").scrollIntoView({behavior:"smooth"});});
  renderSection();
})();
