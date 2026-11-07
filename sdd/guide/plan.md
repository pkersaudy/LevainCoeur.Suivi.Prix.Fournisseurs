# PLAN: work of several batches

Work that takes more than one batch gets `sdd/changes/<slug>.md` and its line in `sdd/roadmap.md`. An issue taken up
moves into the change's why and is deleted.

```markdown
# Search by tag

Why: the reader picks a few tags and gets the articles that carry them.

## Rank articles by matching tags (search)

- Articles that carry every tag come first.
```

One `## <title> (<module>)` section per batch, in order, with the criteria the batch makes true. A fresh reviewer
checks that each batch fits the size limit, touches one module and has testable criteria; the human validates the
plan, which is committed with its first batch. The first section left is the next batch. The batch that empties the
file deletes it and its roadmap line; then a fresh reviewer reads each module the change touched as a whole and
proposes a refactor batch only when it pays.
