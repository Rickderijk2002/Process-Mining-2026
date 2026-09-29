# The denied-loan log

This file is one slice of a Dutch bank's loan process: 3,093 applications that the bank denied, from 1 January 2016 through 5 January 2017. The full process also ends in approval or cancellation. Those endings are absent here, so every story you read from these numbers is a story about a refusal.

Each application is one case. The 124,866 events are about 40 events per application. 2,038 distinct sequences means those 40 events are ordered differently almost every time. There is no single path to memorize. The percentages below answer a different question: in what share of applications does this step appear at least once.

Source files: `data/source/BPI2017Denied(3).xes` and `data/source/BPI2017Denied_petriNet.pnml`. The Petri net is the normative model those traces are compared with. What the pipeline does with them is in [pipeline.md](pipeline.md).

## Three records of the same application

The log does not contain three processes. It records three objects that move together.

| Prefix | What it is | Events |
|---|---|---|
| `A-` | Status of the application | 23,291 |
| `O-` | Status of an offer made on that application | 18,934 |
| `W-` | A work item an employee is doing | 76,455 |

`start` and `end` are the other 6,186 events (3,093 times 2). They are bookends around each case. In the inspection script they land in a leftover bucket whose first letter prints as `o`. That is not a fourth kind of work.

`W-` dominates the event count because one task emits a chain of lifecycle events. The suffix is the state of that task, not a new task.

| Suffix | Meaning |
|---|---|
| `schedule` | Queued |
| `start` | An employee picks it up |
| `suspend` / `resume` | Paused, then continued |
| `complete` | Finished |
| `ate_abort` | The workflow engine aborts it |
| `withdraw` | Taken out of the queue |

Collapse the suffix and there are seven tasks: complete the application, validate it, call after offers, handle leads, call about incomplete files, assess fraud, and a shortened completion that appears in 3 cases.

## The spine of a denied application

These steps are in essentially every case, so they are the backbone.

1. `start`.
2. The application is created (`A-Create-Application`, `A-Concept`) and taken into processing (`A-Accepted`). `A-Accepted` is in all 3,093 denied cases, so here it is an early status. The decision in this file is `A-Denied`, once per case.
3. Someone is assigned to finish the file (`W-Complete-application-schedule`, 100%).
4. An offer is still created (`O-Create-Offer`, `O-Created`, 100%) and almost always sent (`O-Sent-mail-and-online`, 98.4%).
5. The offer usually comes back (`O-Returned`, 94.3%) and is refused (`O-Refused`, 99.2%). `O-Refused` is the offer. `A-Denied` is the application. Both are recorded because they are different objects.
6. A call after the offer is queued and started (99%), then aborted in 98.1% of cases. It is completed in 28 applications (0.9%).
7. `A-Denied`, then `end`.

The log description's successful path ends with the application approved and activated. This subset stops at the refusal, after the offer has already been made and sent.

## Where cases split

Several application states line up exactly with a work item. That pairing is the useful way to read the rest of the activity table.

| Application state | Same share | Work that follows |
|---|---|---|
| `A-Submitted` 72.6% | 72.6% | `W-Handle-leads` is scheduled. About half of those leads are withdrawn (52.1%), a fifth are completed (20%). |
| `A-Incomplete` 34.0% | 34.0% | `W-Call-incomplete-files` is scheduled and started. There is no completed version of this call in the denied log. It is paused and then aborted (30.6%). |
| `A-Validating` 95.6% | 95.6% | `W-Validate-application` is scheduled and started. It is completed in 61.7% and aborted in 49.8%. Those two overlap, so some applications both finish a validation and abort another one. |
| `A-Complete` 99.0% | 99.0% | `W-Call-after-offers` is scheduled. That is the call that is almost always aborted. |

`W-Complete-application` itself is messy. It is scheduled for everyone and started for 94.6%, but completed for only 57.7% and aborted for 36.9%, with a lot of suspend and resume in between. The clerk work is often interrupted.

Two smaller branches sit off to the side. Fraud assessment appears in 132 applications (4.3%) and is never completed in this file. Offer cancelled appears in 149 applications (4.8%), beside the refusals. Shortened completion is 3 applications.

## What the numbers are for

The normative shape is stable: create, accept into processing, make and send an offer, refuse the offer, deny the application. The variation that can explain duration sits in the work items: calls and validations that are aborted, suspended, or repeated, plus the incomplete-file and lead branches that only some cases enter. Sequence identity will not summarize this. Two thousand different orders is why the encoding counts model moves and log moves per activity, instead of treating the activity string as the feature.
