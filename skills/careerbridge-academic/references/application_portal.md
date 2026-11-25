# Academic job portal protocol

## Multi-step form mapping
For every step record portal URL, heading, field text, response type, required flag, allowed options, visible character count, source for answer, proposed answer, state `Ready/Pending/Unknown/Not applicable`, and whether file upload is necessary. Preserve the portal's original choices rather than replacing them with convenient labels.

Typical sections: personal information, citizenship/visa and contact, education/degrees, certifications, academic appointments, teaching/research experiences, professional references, declarations, supporting documents, review and submission. Portal names and sequence differ by employer; only map observed fields.

## Validation
- Double-check title, posting number and position number against current vacancy.
- Use exact legal name as authorized; do not infer passport, visa, nationality, criminal/background, medical or equal-opportunity answers.
- Dates must be internally consistent across positions, education and CV; roles may overlap legitimately but require precise descriptions.
- Degree field, award month/year, awarding institution, mode, accreditation/equivalence require evidence; don't conflate Ph.D. specialization with bachelor's degree major.
- Preserve uploaded file format, filename, size and validity constraints; never promise unsupported uploads succeeded.
- Distinguish **draft**, **saved**, **submitted**, **confirmation obtained**, **under review**. No change in status without portal evidence.

## Deliverables
Create a fill-in worksheet, clear per-step checklist, copy-ready short responses and a list of only unresolved mandatory fields. Submitting, signing declarations, making payment or emailing a referee requires express user authorization and a supported tool.

