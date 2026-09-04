const API_URL = "http://127.0.0.1:8001";
let cache = {credits:[], loans:[], frauds:[], customers:[], contacts:[]};

if (sessionStorage.getItem("adminLoggedIn") !== "true") {
  window.location.href = "admin-login.html";
}

document.getElementById("adminName").textContent = sessionStorage.getItem("adminUsername") || "Admin";

document.querySelectorAll(".nav-item").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach(x => x.classList.remove("active"));
    document.querySelectorAll(".section").forEach(x => x.classList.remove("active"));
    btn.classList.add("active");
    const section = document.getElementById(btn.dataset.section);
    section.classList.add("active");
    document.getElementById("pageTitle").textContent = btn.innerText.trim();
    document.getElementById("pageSubtitle").textContent = subtitle(btn.dataset.section);
  });
});

function subtitle(s){
  return ({
    overview:"Live information coming from FastAPI + PostgreSQL",
    credit:"Complete credit score prediction history",
    loan:"Complete loan default prediction history",
    fraud:"Complete fraud detection history",
    customer:"Complete customer recommendation history",
    contacts:"Customer support and contact history",
    all:"Combined prediction history"
  })[s] || "";
}
function esc(v){return String(v ?? "").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));}
function money(v){return Number(v||0).toLocaleString("en-IN");}
function date(v){return v ? new Date(v).toLocaleString("en-IN") : "—";}
function badge(text,type){return `<span class="badge ${type}">${esc(text)}</span>`;}
function empty(id, cols, text="No records found."){document.getElementById(id).innerHTML=`<tr><td colspan="${cols}" class="muted" style="text-align:center;padding:35px">${text}</td></tr>`;}

async function getJSON(path){
  const r = await fetch(`${API_URL}${path}`);
  if(!r.ok) throw new Error(`${path} returned ${r.status}`);
  return r.json();
}

async function loadAllData(){
  try{
    const [summary, credits, loans, frauds, customers, contacts, health] = await Promise.all([
      getJSON("/admin/summary"),
      getJSON("/get_credit_data"),
      getJSON("/get_loan_data"),
      getJSON("/get_fraud_data"),
      getJSON("/get_customer_data"),
      getJSON("/get_contacts"),
      getJSON("/")
    ]);
    cache={credits,loans,frauds,customers,contacts};
    renderSummary(summary,health);
    renderCredits(credits); renderLoans(loans); renderFrauds(frauds); renderCustomers(customers); renderContacts(contacts); renderAll();
  }catch(e){
    console.error(e);
    document.getElementById("healthBox").innerHTML = "⚠ Unable to connect to FastAPI. Start Uvicorn on port 8000.";
    document.getElementById("healthBox").style.background="#fff0f1";
    document.getElementById("healthBox").style.color="#d94758";
  }
}

function renderSummary(s,health){
  document.getElementById("totalPredictions").textContent=s.total_predictions||0;
  document.getElementById("totalCredits").textContent=s.credits||0;
  document.getElementById("totalLoans").textContent=s.loans||0;
  document.getElementById("totalFrauds").textContent=s.frauds||0;
  document.getElementById("totalCustomers").textContent=s.customers||0;
  document.getElementById("highRisk").textContent=s.high_risk||0;
  const max=Math.max(s.credits,s.loans,s.frauds,s.customers,1);
  [["Credit",s.credits],["Loan",s.loans],["Fraud",s.frauds],["Customer",s.customers]].forEach(([n,v])=>{
    document.getElementById("bar"+n).style.width=((v/max)*100)+"%";
    document.getElementById("bar"+n+"Text").textContent=v;
  });
  document.getElementById("healthBox").innerHTML=`<b>✓ FastAPI Online</b> • ${esc(health.database)} • ML models loaded`;
}

function renderCredits(data){
  if(!data.length)return empty("creditBody",14,"No credit predictions have been stored yet.");
  document.getElementById("creditBody").innerHTML=data.map(x=>`<tr>
    <td>#${x.id}</td><td>${x.age}</td><td>${esc(x.gender)}</td><td>₹${money(x.annual_income)}</td>
    <td>${x.employment_years} yrs</td><td>₹${money(x.monthly_income)}</td><td>₹${money(x.existing_loan)}</td>
    <td>₹${money(x.emi)}</td><td>${x.credit_card_utilization}%</td><td>${x.missed_payments}</td>
    <td>₹${money(x.savings)}</td><td>${x.loan_history}</td><td><b>${Math.round(x.predicted_credit_score)}</b>/900</td><td>${date(x.created_at)}</td>
  </tr>`).join("");
}
function renderLoans(data){
  if(!data.length)return empty("loanBody",11,"No loan default predictions have been stored yet.");
  document.getElementById("loanBody").innerHTML=data.map(x=>`<tr>
    <td>#${x.id}</td><td>${x.age}</td><td>₹${money(x.income)}</td><td>₹${money(x.loan_amount)}</td><td>₹${money(x.emi)}</td>
    <td>${x.employment_years} yrs</td><td>${x.credit_score}</td><td>${x.previous_defaults}</td><td>${x.debt_to_income}%</td>
    <td>${badge(x.prediction,x.prediction==="Loan Default"?"bad":"good")}</td><td>${date(x.created_at)}</td>
  </tr>`).join("");
}
function renderFrauds(data){
  if(!data.length)return empty("fraudBody",10,"No fraud predictions have been stored yet.");
  const tmap={0:"Card",1:"IMPS",2:"NEFT",3:"UPI"}, lmap={0:"Bengaluru",1:"Delhi",2:"Mumbai",3:"Pune"}, dmap={0:"ATM",1:"Mobile",2:"Web/Laptop"};
  const mmap={0:"Electronics",1:"Food",2:"Fuel",3:"Retail/Entertainment",4:"Travel"};
  document.getElementById("fraudBody").innerHTML=data.map(x=>`<tr>
    <td>#${x.id}</td><td>₹${money(x.amount)}</td><td>${tmap[x.transaction_type]??x.transaction_type}</td>
    <td>${lmap[x.location]??x.location}</td><td>${dmap[x.device]??x.device}</td><td>${x.hour}:00</td>
    <td>${mmap[x.merchant_category]??x.merchant_category}</td><td>${x.international===1?"Yes":"No"}</td>
    <td>${badge(x.prediction,x.prediction==="Fraud Transaction"?"bad":"good")}</td><td>${date(x.created_at)}</td>
  </tr>`).join("");
}
function renderCustomers(data){
  if(!data.length)return empty("customerBody",9,"No customer recommendations have been stored yet.");
  document.getElementById("customerBody").innerHTML=data.map(x=>`<tr>
    <td>#${x.id}</td><td>${x.age}</td><td>₹${money(x.income)}</td><td>₹${money(x.savings)}</td><td>${x.credit_score}</td>
    <td>₹${money(x.loan_amount)}</td><td>${x.spending_score}</td><td>${badge(x.recommended_segment,"info")}</td><td>${date(x.created_at)}</td>
  </tr>`).join("");
}
function renderContacts(data){
  if(!data.length)return empty("contactBody",6,"No support messages have been stored yet.");
  document.getElementById("contactBody").innerHTML=data.map(x=>`<tr>
    <td>#${x.id}</td><td><b>${esc(x.name)}</b></td><td>${esc(x.email)}</td><td>${badge(x.department||"General","warn")}</td>
    <td style="white-space:normal;min-width:280px">${esc(x.message)}</td><td>${date(x.created_at)}</td>
  </tr>`).join("");
}
function renderAll(){
  const rows=[];
  cache.credits.forEach(x=>rows.push({m:"Credit Score",id:x.id,input:`Age ${x.age}, Income ₹${money(x.annual_income)}`,result:`${Math.round(x.predicted_credit_score)}/900`,date:x.created_at}));
  cache.loans.forEach(x=>rows.push({m:"Loan Default",id:x.id,input:`Loan ₹${money(x.loan_amount)}, EMI ₹${money(x.emi)}`,result:x.prediction,date:x.created_at}));
  cache.frauds.forEach(x=>rows.push({m:"Fraud Detection",id:x.id,input:`Amount ₹${money(x.amount)}, Hour ${x.hour}`,result:x.prediction,date:x.created_at}));
  cache.customers.forEach(x=>rows.push({m:"Customer Recommendation",id:x.id,input:`Income ₹${money(x.income)}, Credit ${x.credit_score}`,result:x.recommended_segment,date:x.created_at}));
  rows.sort((a,b)=>new Date(b.date||0)-new Date(a.date||0));
  if(!rows.length)return empty("allBody",5);
  document.getElementById("allBody").innerHTML=rows.map(x=>`<tr><td>${badge(x.m,"info")}</td><td>#${x.id}</td><td>${esc(x.input)}</td><td><b>${esc(x.result)}</b></td><td>${date(x.date)}</td></tr>`).join("");
}

function logout(){
  sessionStorage.removeItem("adminLoggedIn");
  sessionStorage.removeItem("adminUsername");
  window.location.href="admin-login.html";
}
loadAllData();
// setInterval(loadAllData,30000);
