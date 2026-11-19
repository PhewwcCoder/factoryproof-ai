# FactoryProof design system

Software / source-grounded factory evidence reconciliation. The brief's warm paper, navy and muted teal establish the palette. The main action is Open demo workspace. The central visual is actual evidence comparison UI.

Colors: paper #f6f7f3, white #ffffff, navy #172e38, teal #256d60, pale teal #e9f1ec, gray #596c73, border #dce2dc, amber #92651d and amber paper #fff4dc. Status colors always accompany text and icons. No gradients, decorative charts, glass or fabricated metrics.

Type: locally served Manrope for headings and DM Sans for body. Display 64/1.08 desktop, 38/1.15 mobile. Workspace h1 32, h2 24, h3 18; body 16/1.6, labels 14, secondary metadata 13. Numeric facts use tabular figures.

Spacing: 4, 8, 12, 16, 24, 32, 48, 64, 96. Application uses a 232px sidebar and fluid main area with 40px gutters; mobile uses a native expandable menu. Landing page uses equal 80px gutters at 1440 and 24px at mobile. Radius 6px controls, 10px panels, 14px large app frame. Borders separate evidence rows. Shadows only on the hero app frame and inspection dialog.

Composition: left-aligned product explanation above a full-width comparison window, then the extraction/verification workflow. Dense evidence rows and aligned buyer columns carry the application. Status summaries are useful counts from the actual current run. Avoid repeated KPI cards. Comparison rows expand into citations and explicit checks.

Motion: a single 240ms hero entrance, 160ms button/row interactions and dialog opening. All nonessential motion disabled with prefers-reduced-motion. Motion Primitives transition-panel pattern inspected; CSS is sufficient for these short state transitions.

Accessibility: visible labels, native buttons/links/dialog, skip link, clear keyboard focus, text statuses, live async messages, 44px targets, no hover-only information. Tables scroll only inside a labeled region; mobile comparison becomes stacked buyer results. No artificial viewport heights on workflow pages.

Skill precedence: the user's functional SaaS, synthetic labeling and restrained-motion requirements override Taste's static-export, random effect, full-screen marketing-section and no-sample-label defaults. Taste contributes real UI, consistent tokens, equal edges, plain copy and browser refinement. No simulated AI claims.
