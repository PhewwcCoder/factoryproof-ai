# Design and verification audit

Applied Taste, Karpathy coding guidelines, frontend-design, React best practices and web interface guidelines. The design uses locally served Manrope/DM Sans, warm neutral surfaces, navy text, restrained green actions, clear status labels and source-first inspection. Existing video material is preserved under video/.

Browser screenshots inspected: landing desktop/mobile, comparison, PDF preview. Responsive navigation overflow found by the first browser run was corrected. Native dialogs support Escape and modal focus; reduced motion is respected. Checkbox controls, visible focus, labels and textual outcomes complement icons/colors.

The Taste quick checker ran but did not certify the page: it reported 28 findings against its prescriptive marketing-page rules, including full-screen section heights, photographs/visual moments, split alignment and a container false positive despite existing .wrap elements. Its mobile nav finding was corrected. The software dashboard intentionally uses compact tables, source excerpts and functional controls rather than adopting the skill's marketing composition rules. This is a partial skill audit, not a claimed gate pass.

Core validation uses actual PDF extraction and independent expected outcomes. The missing original supplied CSV remains a documented limitation. Production verification is recorded separately in deployment.md.
