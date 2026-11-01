# Rename to "choir-practice": what is left

Done: texts, skill folder `choir-practice/`, `choir-practice.skill`, skill name, package names (`Choir_Practice`, `Chor_Uebungen`), CI paths, Dependabot, `CHOIR_PRACTICE_REQ`. What is left depends on the GitHub repository name `vbth/choir-practice`. Change it in one step after renaming the repository:

- Website URL `https://vbth.github.io/choir-practice/` and `/en/`: `SITE` in `site/build_site.py` (canonical, hreflang, `og:`, JSON-LD and `docs/sitemap.xml` are generated), and the two links in the four READMEs.
- Repository URL: `GH` in `site/build_site.py`, `common.MD_LABEL` (EU label for Markdown), the label links at the end of the four READMEs.
- Release downloads of v1.0.0: `ZIPS` in `site/build_site.py` and the example links in the four READMEs. The two example ZIPs carry the old package names (`Chor_Probenpaket`, `Choir_Rehearsal_Pack`); they change with the next release, then update `ZIPS` and `REL`.
- On GitHub itself: repository name, description, topics, Pages address.
