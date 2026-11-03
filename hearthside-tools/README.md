# Hearthside Tools — sales funnel page

Single self-contained landing page for the Hearthside Printables micro-tool
catalog (GapCheck, pdfdesk, FlipCheck, jsonfix, QRForge, SubCut, CSVSweep +
the $29 all-tools bundle). It is the destination link for the distribution
pack posts in `~/workspace/hearthside-tools-batch2/distribution-pack.md`.

## Where it lives

This folder sits inside the existing GitHub Pages user-site repo:

- Repo: `midnightmichigan/midnightmichigan.github.io`
- Local clone: `~/workspace/muse-code-page-deploy/repo/`
- Page: `hearthside-tools/index.html` (same per-page-folder convention as
  `muse-invite-code/` and `printables/`)
- Live URL after deploy: https://midnightmichigan.github.io/hearthside-tools/

A mirror copy is kept at `~/workspace/hearthside-site/` for reference; the
repo copy above is canonical. Edit the repo copy, then re-copy if the mirror
is needed.

## Deploy (run when egress allows a push)

```bash
cd ~/workspace/muse-code-page-deploy/repo
# one-time only, if this clone has no git identity yet:
# git config user.email "dakotamccall200@gmail.com"
# git config user.name "midnightmichigan"
git add hearthside-tools/
git commit -m "Add Hearthside Tools funnel page"
git push origin master
```

GitHub Pages publishes automatically from `master`; the page is live at the
URL above within a minute or two of the push. Verify with:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://midnightmichigan.github.io/hearthside-tools/
```

Expect `200`.

## Links on the page (verified against the listing files, 2026-11-02)

| Item | Price | URL |
|---|---|---|
| GapCheck | $9 | https://payhip.com/b/NCFE5 |
| pdfdesk | $12 | https://payhip.com/b/iruUY |
| FlipCheck | $9 | https://payhip.com/b/N0svT |
| jsonfix | $12 | https://payhip.com/b/xjOo3 |
| QRForge | $7 | https://payhip.com/b/E9tcI |
| SubCut | $9 | https://payhip.com/b/5Uvbh |
| All-tools bundle | $29 | https://payhip.com/b/KOFuD |
| Store root | — | https://payhip.com/u1790829402217713798626 |

Bundle math: the bundle contains the six original tools
(9 + 12 + 9 + 12 + 7 + 9 = $58 separately) at $29, a $29 saving.
CSVSweep ($9) is **not** in the bundle yet and has no live Payhip page yet,
so its card links to the store root and says so. When CSVSweep gets its own
`/b/` page: swap its card link, and if it joins the bundle, update the
bundle math on the page (seven singles = $67).
