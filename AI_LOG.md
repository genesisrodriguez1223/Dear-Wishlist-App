# AI Prompt-and-Diff Log

## Milestone 1

AI Tool: OpenCode

Prompt:
What exactly is Flask in python and what does it do?

Diff / Changes Made:
No code changes were made.
## Milestone 2 - Requirements and AI Elicitation

**AI Tool:** Claude

Prompt:
I'm creating an app that's called Dear Wishlist. It allows for users to track items they would like to buy and save it based on category. Can you please elicit some requirements for my app concept?

AI Response:
I'd love to help nail down the requirements for Dear Wishlist. Let me ask a few quick questions to shape the direction.

**Who's the primary user for this app?**  
General consumers (public app)

**What platform are you targeting first?**  
Web app

**Which core features matter most beyond basic tracking?**  
Priority ranking within categories

Great, that gives me a clear picture: **Dear Wishlist** — a public web app for general consumers to track and categorize items they want to buy, with priority ranking as a standout feature.

Here's a requirements draft based on that:

#### Core Features

- Add items with name, price, URL/link, image, category, and notes
- Organize items into user-defined categories (e.g., "Home," "Tech," "Gifts for Mom")
- Priority ranking within each category (drag-to-reorder or high/medium/low tags)
- Mark items as purchased/archived without deleting them
- Search and filter by category, price range, or priority

#### Account & Data

- User authentication (email/password, or social login)
- Persistent storage tied to user account
- Edit/delete items and categories

#### Nice-to-Haves to Consider

- Auto-fetch item image/price/title from a pasted product URL
- Price drop tracking or alerts
- Shareable read-only wishlist links (even if not collaborative, "share my list" is common for gift-giving)
- Sorting by price, date added, or priority
- Simple analytics (e.g., "total value of your wishlist," "most-wanted category")

#### Design Considerations

- Since it's a public consumer app, onboarding needs to be frictionless (maybe guest mode before requiring signup?)
- Mobile-responsive web design even though mobile app isn't v1
- Empty states matter a lot for a wishlist app — first impression when there's nothing saved yet

A few things worth deciding before you build:

1. **Sharing** — even though you didn't flag it as a top feature, wishlist apps often live or die on shareability (think wedding registries, birthday gift lists). Is that truly out of scope for v1, or just not urgent?

2. **Monetization** — is this free, ad-supported, or do you see affiliate links (Amazon Associates, etc.) as part of the business model? That affects whether URL-import is worth prioritizing.

3. **Priority ranking mechanic** — do you want simple tags (High/Med/Low) or a full drag-and-drop ranked list within each category? These have very different UX complexity.

Want me to turn this into a structured PRD document, or would you rather talk through the open questions first?

### Diff / Changes

No changes were made to my requirements after using Claude. Claude suggested additional features such as user accounts, sharing wishlists, price drop alerts, and analytics, but I decided not to add these features because they were not part of the plan.
