This architecture is better because we separate the databases so that there is not one persistence service as a single point of failure. 

We have the following databases:
- Users (User Information and Authentication)
- Cart (User Cart) (can be Redis)
- Image (Object Store)
- Inventory 
- Orders
- Product Information (static)
- Shipping (Shipping Information)

If one database fails the others are still usable.

Before we had the following failure scenarios:
- If Auth fails:
    1. All users cannot add items to the cart
    2. All users cannot login
    3. All users cannot order their items

- If Image fails:
    1. All users cannot see images.

- If Recommender fails:
    1. All users cannot see recommendations

- If Persistence fails:
    1. All users cannot see categories.
    2. All users cannot see products.
    3. All users cannot login.
    4. All users cannot order their items.
    5. All users cannot see their orders.
    6. All users cannot see their profile details.

The webui is also the gateway in both implementations so if it fails the user cannot use the site at all.
However the webui is stateless and therefore can be scaled horizontally.

After the changes we have the following failure scenarios:
- If Cart fails:
    1. All Users cannot add items to the cart
    2. All Users cannot order their items

- If Image fails:
    1. All users cannot see product and category images.

- If Inventory fails:
    1. All users cannot order products. 

- If Notification fails:
    1. All users dont get a confirmation email.

- If Order fails:
    1. All users cannot order their items.
    2. All users cannot see their orders.
    3. All users cannot see recommendations.

- If Payment fails:
    1. All users cannot order their items.

- If Product fails:
    1. All users cannot see product details.
    2. All users cannot see categories.

- If Recommender fails: TODO recommender should always show most popular items.
    1. All users cannot see recommendations

- If Shipping fails:
    1. All users cannot see their shipping status.

- If User fails:
    1. new users cannot login, however already logged in users can still use the site and not logged in users can still shop.
    2. All users cannot see their profile details.

We can see that each service only has a small impact on the system and only influences 1 or 2 items. Most of these things can be mitigated with caching and graceful degradation. this will be implemented next.

Graceful degradation:
**DONE** If image fails to load, show a generic image. and also implement javascript so that it tries to reload the image later if it detects a not loaded image.

**DONE** if product fails do placeholder, cache categories at webui to show at least some categories. and also cache top 100 products. 

**DONE** if recommender fails just fetch random products from product service or use cached recommendations. make the recommender cache its calculations.

**DONE** if user fails we can store the most important informations in the session? also on login store the user details in the session and then use that to render the page.

If cart fails add it to the user session and then later add it back to the cart service.

If inventory fails, guess that there is enough stock and complete the order and if there is not enough stock send a sorry email. (or just delay the order processing) (MESSAGE QUEUE or Temporal)

if notification fails just skip it or try again later (MESSAGE QUEUE or Temporal).

if order fails this is bad. put the orders in a queue. (MESSAGE QUEUE or Temporal). we need to revert all changes if something in the order process doesnt work. also put the latest orders in the session cookie, so that the user can see its last 3 orders or something.

if payment fails this is bad, however this is stateless and more an api call than something else. just retry.

if shipping fails do it later (MESSAGE QUEUE or Temporal).




After these implementations we shrink the fault potential for every service:
- If Cart fails:
    1. All Users cannot order their items and have to put them in again.

- If Image fails:
    1. All users cannot see only uncached product and category images.

- If Inventory fails:

- If Notification fails:

- If Order fails:

- If Payment fails:

- If Product fails:
    1. All users cannot see only uncached product details and categories.

- If Recommender fails:

- If Shipping fails:
    1. All users cannot see their shipping status.

- If User fails:
    1. new users cannot login, however already logged in users can still use the site and not logged in users can still shop.


It would be also possible to move the cart to the session, however we already store some unimportant data to the user session and with a cart service we make sure that we can run analysis on the carts.

# Alternative

Store everything in the users datastore and have only the async part as a service and maybe the recommender and if it fails use a random product. store a version number and try to update it on the client side. we need javascript and modern browser features for that.