# Regression Cases

Track cases that must not regress:

- restore into non-empty workspace must fail,
- archive must not delete workspace if zip is missing or empty,
- blueprint must not use px units,
- operator must not use `whtml_builder`,
- PM must not continue to Webflow build before approval,
- QA must not approve without Webflow state evidence.

