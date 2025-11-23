# Review System Update Plan for Product Details Page

## Information Gathered
- The ReviewRating model in store/models.py manages reviews with fields for rating, title, body, verified_purchase, status, timestamps, moderation info, and helpfulness votes.
- The Order model in carts/models.py manages orders with statuses but no explicit "refunded" status; "Cancelled" may imply no longer valid purchase.
- The product_detail view in store/views.py fetches product, reviews (status='visible'), purchase flag, and passes to ecommerce/templates/store/product_detail.html for rendering.
- The product_detail.html template shows review summary, verified badges, review form with submission constraints for authentication and purchase.
- The submit_review view exists in both reviews/views.py (with strong server-side purchase enforcement) and store/views.py (with loose enforcement).
- Frontend lacks review list pagination, sorting controls, percent verified in summary, and prefilled review form for edits.
- Moderation is present with statuses and queue but admin interface enhancements and user flagging may be incomplete.

## Plan

### 1. Visibility & Display
- [ ] Modify store/views.py product_detail:
  - Add review sorting parameter (newest, highest rating, lowest rating, most helpful).
  - Implement server-side pagination or "Load more" for reviews.
  - Calculate percent verified (verified_purchase reviews / total visible reviews).
  - Include variables for summary header: average rating, total reviews, percent verified.
- [ ] Update ecommerce/templates/store/product_detail.html:
  - Add sort controls for reviews.
  - Add pagination or "Load more" button.
  - Show percent verified in review summary header.
  - Ensure verified purchase badge displayed.

### 2. Submission UI States and Copy
- [ ] Modify store/views.py:
  - In product_detail, check if user has existing review and pass it to template.
- [ ] Modify ecommerce/templates/store/product_detail.html:
  - Prefill review form if user has existing review.
  - Change submit button text to "Update review" if editing.
  - Show note "You can edit your review" when user is updating.
  - Show messages conditionally for guests, non-buyers, and verified buyers.
  - Show "Your review is pending approval" after submission if moderated (in review submission response).
  
### 3. Submission Rules & Server-Side Behavior
- [ ] Consolidate review submission logic in one view (preferably reviews/views.py):
  - Enforce authentication and purchase check.
  - Validate rating values server-side.
  - Update existing review if present.
  - Ensure verified_purchase flag is set based on purchase check only.
  - Set status field appropriately (pending or approved).
  - Implement rate limiting, spam detection.
  
### 4. Moderation & Flags
- [ ] Enhance admin.py (reviews/admin.py or store/admin.py):
  - Add bulk actions for approving/rejecting reviews.
  - Add filters for status, rating, verified purchase flag.
- [ ] Add front-end support for users to flag reviews.
- [ ] Implement review flag queue for moderators.
- [ ] Use ReviewAudit model to track moderation actions.
- [ ] Implement optional auto-approve rules based on trust thresholds.

### 5. Data Model and Integrity
- [ ] Verify and enforce unique constraint on (product, user) in ReviewRating model.
- [ ] Use transactions when creating/updating reviews to avoid race conditions.
- [ ] Implement process/update to handle refunds (marking reviews accordingly).
- [ ] Implement soft-delete support for reviews, preserving audit trail.

### 6. Analytics, UX Polish, and Operations
- [ ] Compute and cache aggregated review metrics on product model via signals or background jobs.
- [ ] Improve microcopy and affordances including helpful votes UX.
- [ ] Implement anti-abuse measures: rate limit submissions, require account/email verification for first review, CAPTCHA for suspicious activity.
- [ ] Add unit and integration tests for purchase-check logic, uniqueness, moderation transitions, and form flows.
- [ ] Add monitoring for review submission rates, moderation queue, suspicious activity.
- [ ] Implement feature flags for moderation changes rollout with partial subset release and monitoring.

## Dependent Files to Edit
- store/views.py
- reviews/views.py (consolidate/clean submit_review logic)
- ecommerce/templates/store/product_detail.html
- reviews/forms.py (optional validation enhancements)
- reviews/admin.py or store/admin.py (moderation improvements)
- Possibly JavaScript files for UI enhancements and AJAX
- test_reviews.py or similar test files

## Followup Steps After Edits
- [ ] Run all tests and fix issues.
- [ ] Conduct manual QA across user states (guest, non-buyer, buyer).
- [ ] Rollout with feature flags and monitor metrics.
- [ ] Gather feedback and iterate.


# Next actions after plan approval:
- Break into incremental implementation steps.
- Implement according to plan and update TODO.md with progress.
