/**
 * Citation-chain validation for the published benchmark data.
 *
 * No seeding: every record must carry a full citation chain
 * (source → author/date → url/doi → specific reference). A record without a complete chain is a
 * fabricated-looking figure, so `tests-webapp/unit/benchmarks.test.ts` runs this over
 * `data/benchmarks.json` in CI and the suite fails if any record loses a field.
 *
 * This used to live in `lib/etl/`, where the importer rejected uncited records at import time. The
 * database and the importer are gone; the control is not, because the reason for it was never the
 * database — it was that a number with no source is worse than no number.
 */

/**
 * One benchmark record's citation chain.
 *
 * Named `CitationChain` rather than `Citation` because `lib/valuation/citations.ts` already exports a
 * `Citation` for a method's published source — a different shape (`id`, `title`, `kind`, `year`) in
 * the same directory. Two exported types with one name and no shared fields is how a `Citation` gets
 * passed where the other is meant.
 */
export interface CitationChain {
  source: string;
  author: string;
  date: string;
  url?: string;
  doi?: string;
  ref: string;
}

export interface CitationError {
  field: string;
  message: string;
}

export function validateCitation(citation: Partial<CitationChain> | null | undefined): CitationError[] {
  const errors: CitationError[] = [];

  if (!citation) {
    return [{ field: "citation", message: "missing citation chain" }];
  }

  if (!citation.source?.trim()) errors.push({ field: "source", message: "missing source" });
  if (!citation.author?.trim()) errors.push({ field: "author", message: "missing author/publisher" });
  if (!citation.date?.trim()) errors.push({ field: "date", message: "missing publication date" });
  if (!citation.url?.trim() && !citation.doi?.trim()) {
    errors.push({ field: "url", message: "missing url or doi" });
  }
  if (!citation.ref?.trim()) errors.push({ field: "ref", message: "missing specific reference" });

  return errors;
}

export function hasValidCitation(citation: Partial<CitationChain> | null | undefined): boolean {
  return validateCitation(citation).length === 0;
}
