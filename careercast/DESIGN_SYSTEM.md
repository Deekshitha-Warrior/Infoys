# CareerCast visual standard

All workspace pages use `DashboardLayout`, the same sidebar and top bar, and
`frontend/src/standard.css`. Login and registration share `AuthVisual` and the
same public-page styles. Do not create a separate visual theme for new routes.

## Shared rules

- Midnight navy navigation and page banners; violet actions and charts;
  pale lavender page backgrounds; white cards with fine borders.
- One heading hierarchy: page title, section heading, field or supporting label.
- Consistent card radius, spacing, buttons, form controls, tables and focus rings.
- Page banners explain the purpose of the page. The dashboard uses the welcome
  illustration, quick actions and career overview instead.
- Responsive grids stack on smaller screens. Navigation becomes a horizontally
  scrollable strip on phones. Tables scroll inside their own card.
- Decorative art has empty alternative text; functional links and buttons keep
  meaningful accessible labels.
- Never invent personality types, proficiency scores, market demand or progress
  to fill a design. Show profile data, measured results, or an explicit empty state.

## Dashboard data

Skill count comes from the current profile. Career matches come from the saved
current prediction. Learning progress uses the same matched skills and locally
saved completed steps as Learning Path. Resume completeness is the existing
eight-check result; it is not an ATS score. Profile completeness uses saved fields.

## Illustration provenance

See `frontend/public/images/ASSETS.md` for the built-in image-generation prompts
and project asset locations. Keep these images local to the project.

## Validation

The production frontend build passes. Dashboard, Career Intelligence, Skill
Analysis, Learning Path, Resume Analyzer, My Profile, Model Evaluation, Settings,
and Help were opened in the existing browser session with no horizontal page
overflow at its desktop width. Login/registration compile with the shared style;
the signed-in user's session was preserved rather than logging them out to test.
