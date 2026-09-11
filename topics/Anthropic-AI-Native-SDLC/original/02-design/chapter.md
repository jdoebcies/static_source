# Design · PDF full text

## Design

Requirements and design collapse into one session. Policy is applied while the spec is written, not discovered in a review weeks later.

### Requirements and design

Once approved by the product owner, Claude takes the accepted intent.md and produces a requirements and design spec. This is guided by the organization's [skills](https://code.claude.com/docs/en/skills) for brand, security, compliance, and UX.

The product owner reviews that spec, but doesn't write it. The goal of this process is to create a spec the engineering team can plan against, with flagged areas of concern.

Front-end work is the clearest example. Once the intent.md is accepted, the product owner mocks the design up in [Claude Design](https://claude.com/product/design) (beta) from the intent.md, iterates on the mock, and then exports it to Claude Code to build.

**Traditional.** Requirements and design are separate phases run by separate teams. Analysts formalize the idea into requirements and designers then parse those back into a design. The separation exists for accountability, but it is slow and lossy.

**AI-native.** Both phases happen in a single prompted session. Claude takes intent.md and produces a requirements and design spec, constrained by the organization's skills, with areas of concern flagged.

#### Getting started

**Prerequisites**

Write an intent.md file, with brand, security, compliance, and UX policies written as skills.

**Infrastructure**

A product owner with Claude access. No engineering skill is required.

#### How to execute it

- The product owner opens a session with the organization's skills available and attaches the intent.md.

- The product owners prompt points at the intent.md, names the constraints, and demands flagged concerns. Run it by hand at first, then codify it as an organization-level slash command. From there make the acceptance of intent.md in the intent home the trigger, with a non-interactive job that fires on the merge, run the pass with the organization's skills loaded, and commit spec.md as a pull request (the CI/CD play in Stage 5: Deploy covers the plumbing). From that point the product owner's first involvement is the review.

- The same product owner reviews the spec against the idea. Does the spec solve the stated problem, and are the open questions from intent.md answered or carried forward?

- Work through the flagged concerns first as they are the points an analyst would have escalated. The product owner resolves each one with its policy owner before engineering sees the spec.

- Commit spec.md alongside intent.md. The file pair records what was asked for and what was decided.

- The product owner decides whether the spec and intent progress to build, consulting a technical lead for anything the organization classes as higher risk. A human team mate always makes this call, and accepting the spec is what starts the plan mode play in Stage 3: Build.

#### What it looks like (the prompt)

```markdown
Read the attached intent.md and produce a requirements and design spec for integrating it into our existing codebase. Apply the skills available to you so the plan conforms to our brand guidelines, security policies and UX standards. Document the spec fully as spec.md, ready to hand to the engineering team. Describe clearly any areas of concern, especially where you cannot satisfy contradicting policies.
```

#### Governance considerations

Instead of being discovered in a review weeks later, the live policy is read and applied while the spec is written. The organization's skills are applied as constraints on the spec. The spec, the prompt that produced it, and the skill versions in force are all logged in version control. The product owner signs off the spec, and routes flagged concerns to the named policy owners.

#### How to measure it

**Leading indicator**

Elapsed time between the intent.md commit and the spec.md commit for the same change (two git timestamps), compared with the old requirements-plus-design cycle.

**Lagging indicator**

Requirements rework after build starts. Count spec.md commits dated after the first plan.md commit for the same change. Git log will give this directly.
