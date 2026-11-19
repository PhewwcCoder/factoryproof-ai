import { z } from 'zod';
import type { Citation, Evidence, Finding, Requirement, Status } from '../lib/types';

const date = z.string().regex(/^\d{4}-\d{2}-\d{2}$/).refine(v => validDate(v), 'Invalid calendar date');
export const requirementSchema = z.object({
  id: z.string().min(1).max(100), buyer_id: z.string().min(1).max(100),
  title: z.string().min(1).max(200), text: z.string().min(1).max(3000),
  evidence_type: z.string().regex(/^[a-z_]+$/).max(80),
  months: z.number().int().min(1).max(120).nullable(), days: z.number().int().min(1).max(3650).nullable().optional(),
  signatures: z.array(z.string().max(80)).max(20), scope: z.string().min(1).max(300),
  minimum_frequency: z.number().min(0).max(100000).nullable(), minimum_value: z.number().min(0).max(1000000).nullable(),
  mandatory_fields: z.array(z.enum(['event_date','expiry_date','scope','period_start','period_end','factory_id','value','frequency'])).max(10),
  period_start: date.nullable(), period_end: date.nullable(), source_reference: z.string().min(1).max(1000), version: z.number().int().positive(),
});
export const runSchema = z.object({ reference_date: date, buyer_ids: z.array(z.string()).min(1).max(10).optional() });
export function validDate(value: string): boolean {
  const d = new Date(value + 'T00:00:00Z');
  return !Number.isNaN(d.getTime()) && d.toISOString().slice(0,10) === value;
}
export function monthsBefore(value: string, months: number) {
  const d = new Date(value+'T00:00:00Z'), day=d.getUTCDate();
  d.setUTCDate(1); d.setUTCMonth(d.getUTCMonth()-months);
  const last = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth()+1,0)).getUTCDate();
  d.setUTCDate(Math.min(day,last)); return d.toISOString().slice(0,10);
}
export function verify(req: Requirement, evidence: Evidence | undefined, reference: string): Pick<Finding,'status'|'checks'> {
  const checks: Finding['checks'] = [], facts=evidence?.facts||{}, citations=evidence?.citations||{};
  const add=(rule:string,status:Status,reason:string,field?:string)=>{
    const citation=field?citations[field]:undefined;
    // An extracted value without a matching passage must never establish support.
    const grounded=!citation || evidence?.pages.some(p=>p.page===citation.page&&p.text.includes(citation.quote));
    checks.push({rule,status:status==='SUPPORTED'&&field&&(!citation||!grounded)?'NEEDS_REVIEW':status,reason:!grounded?'Source citation could not be verified.':reason,citation:grounded?citation||null:null});
  };
  if(!evidence) add('evidence','MISSING','No relevant evidence was found.');
  else {
    if(evidence.processing_status!=='ready') add('extraction','NEEDS_REVIEW','Extraction is incomplete. Inspect the original document.');
    add('type',facts.evidence_type===req.evidence_type?'SUPPORTED':'INSUFFICIENT',`Document type: ${String(facts.evidence_type||'unknown').replaceAll('_',' ')}.`,'evidence_type');
    for(const field of new Set([...req.mandatory_fields,'scope',...((req.months||req.days)?['event_date']:[])])) {
      if(facts[field]===undefined||facts[field]==='') add(field,'NEEDS_REVIEW',`Missing ${field.replaceAll('_',' ')}; a reviewer must resolve it.`);
    }
    if(facts.scope) add('scope',facts.scope===req.scope?'SUPPORTED':'INSUFFICIENT',facts.scope===req.scope?'Evidence covers the required scope.':`Scope is ${facts.scope}; required ${req.scope}.`,'scope');
    if(evidence.conflicts.length) add('conflict','NEEDS_REVIEW',`Conflicting source values: ${evidence.conflicts.join(', ')}.`);
    for(const field of ['event_date','expiry_date','period_start','period_end']) {
      const value=facts[field]; if(!value) continue;
      if(typeof value!=='string'||!validDate(value)){add(field,'NEEDS_REVIEW',`Invalid ${field} in source.`,field);continue;}
      if(field==='event_date') {
        if(value>reference) add('date','NEEDS_REVIEW','Event date is after the assessment date.',field);
        else if(req.months){const cutoff=monthsBefore(reference,req.months);add('date_window',value>=cutoff?'SUPPORTED':'INSUFFICIENT',`${value} ${value>=cutoff?'falls within':'is outside'} the ${req.months}-month window (from ${cutoff}).`,field);}
        if(req.days&&value<=reference){const age=Math.round((Date.parse(reference)-Date.parse(value))/86400000);add('date_window',age<=req.days?'SUPPORTED':'INSUFFICIENT',`${value} is ${age} days old; maximum ${req.days} days.`,field);}
      }
      if(field==='expiry_date') add('expiry',value>=reference?'SUPPORTED':'INSUFFICIENT',`Valid until ${value}; assessed on ${reference}.`,field);
    }
    if(typeof facts.expiry_date==='string'&&typeof facts.event_date==='string'&&facts.expiry_date<facts.event_date) add('chronology','NEEDS_REVIEW','Expiry date precedes the issue date.','expiry_date');
    for(const signature of req.signatures){const present=Array.isArray(facts.signatures)&&facts.signatures.includes(signature), field=citations['signature:'+signature]?'signature:'+signature:'signatures';
      // Absence without an explicit source statement is ambiguous, not proof of failure.
      add('signature',present?'SUPPORTED':citations[field]?'INSUFFICIENT':'NEEDS_REVIEW',`Required ${signature.replaceAll('_',' ')} signature ${present?'recorded':'not recorded'}.`,field);}
    for(const [field,threshold] of [['frequency',req.minimum_frequency],['value',req.minimum_value]] as const){if(threshold!==null){const value=facts[field];add(field,typeof value!=='number'?'NEEDS_REVIEW':value>=threshold?'SUPPORTED':'INSUFFICIENT',`Recorded ${field}: ${value??'unknown'}; required at least ${threshold}.`,field);}}
    for(const [field,required] of [['period_start',req.period_start],['period_end',req.period_end]] as const){if(required){const value=facts[field];const valid=typeof value==='string'&&validDate(value);add(field,!valid?'NEEDS_REVIEW':(field==='period_start'?value<=required:value>=required)?'SUPPORTED':'INSUFFICIENT',`Recorded ${field}: ${value??'unknown'}; required ${required}.`,field);}}
  }
  const status=(['MISSING','NEEDS_REVIEW','INSUFFICIENT'] as Status[]).find(s=>checks.some(c=>c.status===s))||'SUPPORTED';
  return {status,checks};
}

const titles:Record<string,string>={'Fire Drill Exercise Log':'fire_drill','Safety Training Record':'safety_training','Electrical Inspection':'electrical_inspection','Safety Committee Minutes':'worker_committee'};
const labels:Record<string,string>={'Exercise date':'event_date','Training date':'event_date','Inspection date':'event_date','Meeting date':'event_date','Valid until':'expiry_date','Factory code':'factory_id','Facility / unit':'scope','Attendance count':'value'};
const signatures:Record<string,string>={'Safety officer sign-off':'safety_officer','Trainer sign-off':'trainer','Inspector sign-off':'inspector','Management signature':'management_chair','Worker representative signature':'worker_representative'};
export function parsePages(pages: Evidence['pages']): Pick<Evidence,'facts'|'citations'|'conflicts'|'processing_status'|'message'|'extraction_method'|'pages'> {
  const facts:Evidence['facts']={}, citations:Record<string,Citation>={}, conflicts=new Set<string>();
  const save=(field:string,value:string|number|string[],quote:string,page:number)=>{if(field in facts&&JSON.stringify(facts[field])!==JSON.stringify(value))conflicts.add(field);else{facts[field]=value;citations[field]={field,quote,page};}};
  for(const page of pages){const lines=page.text.split('\n');for(let i=0;i<lines.length;i++){
    const line=lines[i].trim(), raw=lines[i+1]?.trim();
    if(titles[line])save('evidence_type',titles[line],line,page.page);
    if(labels[line]&&raw){const field=labels[line], value=field==='value'?Number(raw.match(/^\d+\b/)?.[0]):raw;if(typeof value!=='number'||Number.isFinite(value))save(field,value,line+'\n'+raw,page.page);}
    if(signatures[line]&&raw){const sig=signatures[line],key='signature:'+sig;save(key,raw,line+'\n'+raw,page.page);if(/^Present\b/.test(raw)){const list=Array.isArray(facts.signatures)?facts.signatures:[];facts.signatures=[...new Set([...list,sig])];}}
    const m=line.match(/^([A-Za-z_ ]+):\s*(.+)$/);if(m){const key=m[1].trim().toLowerCase().replaceAll(' ','_'),v=m[2].trim();if(['evidence_type','event_date','expiry_date','scope','signatures','frequency','value','period_start','period_end','factory_id'].includes(key)&&!['unknown','missing','none','not recorded'].includes(v.toLowerCase())){const value=key==='signatures'?v.split(',').map(s=>s.trim().toLowerCase()):['frequency','value'].includes(key)?Number(v):v;if(typeof value!=='number'||Number.isFinite(value))save(key,value,line,page.page);}}
  }}
  return {facts,citations,conflicts:[...conflicts],pages,processing_status:facts.evidence_type?'ready':'needs_review',extraction_method:'Real native PDF text + deterministic field extraction (no fixtures, no hosted LLM)',message:facts.evidence_type?undefined:'No supported structured document type found. Scanned PDFs require OCR; inspect the original and request reviewed extraction.'};
}
