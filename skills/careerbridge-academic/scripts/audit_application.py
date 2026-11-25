#!/usr/bin/env python3
"""Lightweight, offline QA for CareerBridge Academic application CSVs.
Does not authenticate or verify live opportunities, credentials, or portal submissions.
"""
import argparse, csv, json, re
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_STATES = {'Identified','Eligibility checked','Drafting','Ready for review','Submitted','Acknowledged','Shortlisted','Interview','Offer','Rejected','Withdrawn','Closed'}
ALLOWED_ASSESSMENTS = {'Meets','Partial','Not met','Unknown','Not applicable'}
CLAIM_STATES = {'Verified','Self-declared','Pending','Contradicted','Unknown'}

def load_csv(path):
    path=Path(path)
    with path.open('r',encoding='utf-8-sig',newline='') as stream:
        reader=csv.DictReader(stream)
        if not reader.fieldnames: raise ValueError(f'{path.name}: empty CSV header')
        rows=list(reader)
    return set(reader.fieldnames),rows

def check_date(value):
    if not value: return True
    try: date.fromisoformat(value); return True
    except ValueError: return False

def check_url(value):
    if not value:return True
    p=urlparse(value)
    return p.scheme in ('http','https') and bool(p.netloc)

def add(issues, source, row, field, severity, detail):
    issues.append({'source':source,'row':row,'field':field,'severity':severity,'detail':detail})

def audit_tracker(path,issues):
    fields,rows=load_csv(path)
    required={'Opportunity_ID','Institution','Position_Title','Posting_Number','Official_Source_URL','Closing_Date','Date_Checked','Status','Application_URL'}
    for col in sorted(required-fields): add(issues,str(path),1,col,'error','Required column missing')
    dupes=Counter(r.get('Opportunity_ID','').strip() for r in rows if r.get('Opportunity_ID','').strip())
    for i,r in enumerate(rows,2):
        rid=(r.get('Opportunity_ID') or '').strip()
        if not rid: add(issues,str(path),i,'Opportunity_ID','error','Missing opportunity ID')
        if rid and dupes[rid]>1:add(issues,str(path),i,'Opportunity_ID','error','Duplicate opportunity ID')
        if (r.get('Status') or '').strip() not in ALLOWED_STATES:add(issues,str(path),i,'Status','error','Unknown application status')
        for field in ('Date_Checked','Closing_Date'):
            if not check_date((r.get(field) or '').strip()):add(issues,str(path),i,field,'error','Use ISO date YYYY-MM-DD')
        for field in ('Official_Source_URL','Application_URL'):
            if not check_url((r.get(field) or '').strip()):add(issues,str(path),i,field,'error','Malformed URL')
        if not (r.get('Official_Source_URL') or '').strip():add(issues,str(path),i,'Official_Source_URL','warning','No official vacancy evidence link')
        if not (r.get('Closing_Date') or '').strip():add(issues,str(path),i,'Closing_Date','warning','Deadline unknown; verify with employer')
        if (r.get('Status') or '').strip() in ('Submitted','Acknowledged','Shortlisted','Interview','Offer'):
            if not (r.get('Notes') or '').strip() and not (r.get('Next_Action') or '').strip():
                add(issues,str(path),i,'Status','warning','Record verification/confirmation evidence for advanced status')
    return len(rows)

def audit_eligibility(path,issues):
    fields,rows=load_csv(path)
    required={'Criterion_ID','Requirement','Type','Source_URL','Candidate_Evidence','Assessment'}
    for col in sorted(required-fields): add(issues,str(path),1,col,'error','Required column missing')
    for i,r in enumerate(rows,2):
        if (r.get('Assessment') or '').strip() not in ALLOWED_ASSESSMENTS:add(issues,str(path),i,'Assessment','error','Assessment must be Meets/Partial/Not met/Unknown/Not applicable')
        if not (r.get('Source_URL') or '').strip():add(issues,str(path),i,'Source_URL','warning','Employer requirement lacks source URL')
        if (r.get('Assessment') or '').strip()=='Meets' and not (r.get('Candidate_Evidence') or '').strip():add(issues,str(path),i,'Candidate_Evidence','error','Meets requires candidate evidence')
    return len(rows)

def audit_claims(path,issues):
    fields,rows=load_csv(path)
    required={'Claim_ID','Claim_Text','Source_Document','Verification_Status','Can_Use_In_Application'}
    for col in sorted(required-fields): add(issues,str(path),1,col,'error','Required column missing')
    for i,r in enumerate(rows,2):
        status=(r.get('Verification_Status') or '').strip()
        use=(r.get('Can_Use_In_Application') or '').strip().lower()
        if status not in CLAIM_STATES:add(issues,str(path),i,'Verification_Status','error','Use an allowed verification state')
        if use not in ('yes','no'):add(issues,str(path),i,'Can_Use_In_Application','error','Use Yes/No')
        if use=='yes' and status not in ('Verified','Self-declared'):add(issues,str(path),i,'Can_Use_In_Application','error','Cannot use unsupported or contradicted claim')
        if status=='Verified' and not (r.get('Source_Document') or '').strip():add(issues,str(path),i,'Source_Document','error','Verified claim has no evidence source')
    return len(rows)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tracker',type=Path)
    parser.add_argument('--eligibility',type=Path)
    parser.add_argument('--claims',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if not any((args.tracker,args.eligibility,args.claims)):
        parser.error('At least one of --tracker, --eligibility, --claims is required')
    issues=[];counts={}
    for label,fn,path in [('tracker',audit_tracker,args.tracker),('eligibility',audit_eligibility,args.eligibility),('claims',audit_claims,args.claims)]:
        if path:
            try:counts[label]=fn(path,issues)
            except (OSError,ValueError) as e:add(issues,str(path),0,'file','error',str(e))
    result={'checks':counts,'errors':sum(x['severity']=='error' for x in issues),'warnings':sum(x['severity']=='warning' for x in issues),'issues':issues,'disclaimer':'Structural QA only. Sources and external submission statuses require independent verification.'}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    return 1 if result['errors'] else 0
if __name__=='__main__':raise SystemExit(main())

