from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError

with workflow.unsafe.imports_passed_through():
    from activities import get_cart_items, check_and_reserve, get_total_price, simulate_payment, release_items, store_order, dispatch_shipping, set_shipping_id, reset_cart, get_user_email, send_email_notification
    from shared import OrderDetails


@workflow.defn
class ProcessOrder:
    @workflow.run
    async def run(self, order_details: OrderDetails):
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            maximum_interval=timedelta(seconds=2),
            non_retryable_error_types=["NotEnoughInventoryError", "InsufficientFundsError"],
        )
        
        # 1. Get cart items
        cart_items = await workflow.execute_activity(
            get_cart_items, order_details.user_id, start_to_close_timeout=timedelta(seconds=5), retry_policy=retry_policy,
        )
        

        try:
            # 2. Check + reserve inventory
            await workflow.execute_activity(
                check_and_reserve, cart_items, start_to_close_timeout=timedelta(seconds=5), retry_policy=retry_policy,
            )
        except ActivityError as e:
            return {"error": e.message}, 500
        
        # 3. Get product prices
        total_price = await workflow.execute_activity(
            get_total_price, cart_items, start_to_close_timeout=timedelta(seconds=5), retry_policy=retry_policy,
        )

        # 4. Simulate payment
        try:
            await workflow.execute_activity(
                simulate_payment, order_details.user_id, total_price, start_to_close_timeout=timedelta(seconds=5), retry_policy=retry_policy,
            )
        except ActivityError as e:
            await workflow.execute_activity(
                release_items, cart_items, start_to_close_timeout=timedelta(seconds=5), retry_policy=retry_policy,
            )
            return {"error": e.message}, 500

        # 5. Store order
        new_order_id = await workflow.execute_activity(
            store_order, order_details.user_id, total_price, order_details, cart_items, start_to_close_timeout=timedelta(seconds=5), retry_policy=retry_policy,
        )

        # 6. Dispatch shipping
        shipping_id = await workflow.execute_activity(
            dispatch_shipping, new_order_id, order_details, start_to_close_timeout=timedelta(seconds=5), retry_policy=retry_policy,
        )

        # 7. Set shipping id in order
        await workflow.execute_activity(
            set_shipping_id, new_order_id, shipping_id, start_to_close_timeout=timedelta(seconds=5), retry_policy=retry_policy,
        )

        # 8. Reset cart
        await workflow.execute_activity(
            reset_cart, order_details.user_id, start_to_close_timeout=timedelta(seconds=5), retry_policy=retry_policy,
        )
        
        # 9. Send email notification
        ## Get user email
        email = await workflow.execute_activity(
            get_user_email, order_details.user_id, start_to_close_timeout=timedelta(seconds=5), retry_policy=retry_policy,
        )
        
        ## Send message
        await workflow.execute_activity(
            send_email_notification, email, new_order_id, start_to_close_timeout=timedelta(seconds=5), retry_policy=retry_policy,
        )

        return {"success": "yay"}, 200