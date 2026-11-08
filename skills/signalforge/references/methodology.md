# Methodology and statistical limitations

For video `i`, use `views(i) / median(views(neighbors(i)))` when there are at least five valid neighbors from the same creator and platform. The neighborhood consists of up to 10 earlier and 10 later uploads ordered by timestamp and stable ID. No comparison across creators. Exclude videos with missing views, dates or creators from baseline calculation. Missing data stays null, and a zero baseline never receives an artificial multiplier.

The topic signal score is a heuristic ranking based on creator repetition (40%), relative-performance multiplier (40%) and platform breadth (20%). It is **not** a calibrated confidence, growth estimate, expected ROI, forecast or verified impact.

Cautions: platform view definitions differ; channels can have format shifts; fresh uploads have less exposure; selected samples and publication dates can bias apparent outliers; metadata-only analysis cannot confirm spoken hooks, sentiment or product value. Repeated sampling and independent sources are necessary for velocity and claims.

Inspirational attribution: independently implemented neighborhood-median concept described in a Spanish-language viral-video research guide credited to Pedro (2026). This repository does not distribute or copy its PDF.
