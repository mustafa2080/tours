import requests
import json
import uuid
import logging
from django.conf import settings
from django.urls import reverse
from urllib.parse import urljoin
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PayPalClient:
    """
    PayPal API client for handling payment operations.
    """
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_SECRET
        self.mode = settings.PAYPAL_MODE
        self.test_mode = getattr(settings, 'PAYPAL_TEST_MODE', False)

        # Set the base URL based on mode (sandbox or live)
        if self.mode == 'sandbox':
            self.base_url = 'https://api.sandbox.paypal.com'
        else:
            self.base_url = 'https://api.paypal.com'

        logger.info(f"PayPal client initialized. Mode: {self.mode}, Test mode: {self.test_mode}")

    def get_access_token(self):
        """
        Get an access token from PayPal API.
        """
        # Return a fake token in test mode
        if self.test_mode:
            logger.info("Using test mode - returning fake access token")
            return "TEST_ACCESS_TOKEN"

        url = f"{self.base_url}/v1/oauth2/token"
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US"
        }
        data = {
            "grant_type": "client_credentials"
        }

        try:
            logger.info(f"Requesting PayPal access token from {url}")
            response = requests.post(
                url,
                auth=(self.client_id, self.client_secret),
                headers=headers,
                data=data,
                timeout=15  # Increased timeout to prevent hanging
            )

            logger.info(f"PayPal token response status: {response.status_code}")

            if response.status_code == 200:
                token_data = response.json()
                logger.info("Successfully obtained PayPal access token")
                return token_data['access_token']
            else:
                error_msg = f"Failed to get PayPal access token: Status {response.status_code}"
                try:
                    error_details = response.json()
                    error_msg += f", Details: {json.dumps(error_details)}"
                except:
                    error_msg += f", Response: {response.text}"

                logger.error(error_msg)
                raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error when getting PayPal access token: {str(e)}")
            # Fall back to test mode if network error
            logger.warning("Falling back to test mode due to network error")
            return "FALLBACK_TEST_TOKEN"

    def create_order(self, booking):
        """
        Create a PayPal order for a booking with detailed trip information.
        """
        # Test mode handling
        if self.test_mode:
            logger.info("Using test mode - creating fake PayPal order")
            fake_order_id = f"TEST-ORDER-{uuid.uuid4()}"
            return {
                "id": fake_order_id,
                "status": "CREATED",
                "links": [
                    {
                        "href": f"https://www.sandbox.paypal.com/checkoutnow?token={fake_order_id}",
                        "rel": "approve",
                        "method": "GET"
                    },
                    {
                        "href": f"{self.base_url}/v2/checkout/orders/{fake_order_id}",
                        "rel": "self",
                        "method": "GET"
                    },
                    {
                        "href": f"{self.base_url}/v2/checkout/orders/{fake_order_id}/capture",
                        "rel": "capture",
                        "method": "POST"
                    }
                ]
            }

        try:
            # Get access token
            access_token = self.get_access_token()
            url = f"{self.base_url}/v2/checkout/orders"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }

            # Format currency amounts with 2 decimal places
            amount = "{:.2f}".format(float(booking.total_price))
            subtotal = "{:.2f}".format(float(booking.subtotal))
            discount = "{:.2f}".format(float(booking.discount_amount))

            # Get currency from booking or use default
            currency_code = booking.currency_code if hasattr(booking, 'currency_code') else 'USD'

            # Get tour details
            tour_name = getattr(booking.tour, 'name', 'Tour')
            destination = getattr(booking.tour.destination, 'name', '') if hasattr(booking.tour, 'destination') else ''

            # Create description with comprehensive trip details
            description = (
                f"{tour_name} - {destination}\n"
                f"Duration: {booking.tour.duration_days} days\n"
                f"Dates: {booking.start_date.strftime('%b %d')} - {booking.end_date.strftime('%b %d, %Y')}\n"
                f"Participants: {booking.num_adults} Adults"
            )
            if booking.num_children:
                description += f", {booking.num_children} Children"

            # Prepare items array
            items = [
                {
                    "name": f"Adult Ticket - {tour_name}",
                    "description": f"{booking.start_date.strftime('%b %d')} - {booking.end_date.strftime('%b %d, %Y')}",
                    "quantity": str(booking.num_adults),
                    "unit_amount": {
                        "currency_code": currency_code,
                        "value": "{:.2f}".format(float(booking.tour.price))
                    },
                    "category": "DIGITAL_GOODS"
                }
            ]

            # Add children tickets if any
            if booking.num_children:
                child_price = float(booking.tour.price) * 0.5
                items.append({
                    "name": f"Child Ticket - {tour_name}",
                    "description": f"{booking.start_date.strftime('%b %d')} - {booking.end_date.strftime('%b %d, %Y')}",
                    "quantity": str(booking.num_children),
                    "unit_amount": {
                        "currency_code": currency_code,
                        "value": "{:.2f}".format(child_price)
                    },
                    "category": "DIGITAL_GOODS"
                })

            # Prepare the order payload
            payload = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "reference_id": f"booking_{booking.id}",
                        "description": description,
                        "custom_id": str(booking.id),
                        "invoice_id": f"INV-{booking.id}-{uuid.uuid4().hex[:8].upper()}",
                        "amount": {
                            "currency_code": currency_code,
                            "value": amount,
                            "breakdown": {
                                "item_total": {
                                    "currency_code": currency_code,
                                    "value": subtotal
                                },
                                "discount": {
                                    "currency_code": currency_code,
                                    "value": discount
                                }
                            }
                        },
                        "items": items
                    }
                ],
                "application_context": {
                    "brand_name": settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else "Tourism Website",
                    "locale": "en-US",
                    "landing_page": "BILLING",
                    "shipping_preference": "NO_SHIPPING",
                    "user_action": "PAY_NOW",
                    "return_url": settings.SITE_URL + "/payments/confirm/" if hasattr(settings, 'SITE_URL') else "http://localhost:8000/payments/confirm/",
                    "cancel_url": settings.SITE_URL + "/payments/cancel/" if hasattr(settings, 'SITE_URL') else "http://localhost:8000/payments/cancel/"
                }
            }

            # Make the API call
            logger.info(f"Creating PayPal order with payload: {json.dumps(payload)}")
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )

            logger.info(f"PayPal create order response status: {response.status_code}")

            if response.status_code in (200, 201):
                order_data = response.json()
                logger.info(f"PayPal order created successfully: {order_data['id']}")
                return order_data
            else:
                error_msg = f"Failed to create PayPal order: Status {response.status_code}"
                try:
                    error_details = response.json()
                    error_msg += f", Details: {json.dumps(error_details)}"
                except:
                    error_msg += f", Response: {response.text}"

                logger.error(error_msg)
                raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error when creating PayPal order: {str(e)}")
            if self.test_mode:
                logger.warning("Falling back to test mode due to network error")
                fake_order_id = f"TEST-ORDER-{uuid.uuid4()}"
                return {
                    "id": fake_order_id,
                    "status": "CREATED",
                    "links": [
                        {
                            "href": f"https://www.sandbox.paypal.com/checkoutnow?token={fake_order_id}",
                            "rel": "approve",
                            "method": "GET"
                        }
                    ]
                }
            else:
                raise

    def capture_order(self, order_id):
        """
        Capture a PayPal order payment.
        """
        # Test mode handling
        if self.test_mode:
            logger.info(f"Using test mode - simulating capture for order {order_id}")
            return {
                "id": f"CAPTURE-{uuid.uuid4()}",
                "status": "COMPLETED",
                "purchase_units": [
                    {
                        "reference_id": f"booking_test",
                        "payments": {
                            "captures": [
                                {
                                    "id": f"CAPTURE-{uuid.uuid4()}",
                                    "status": "COMPLETED",
                                    "amount": {
                                        "value": "100.00",
                                        "currency_code": "USD"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }

        try:
            # Get access token
            access_token = self.get_access_token()
            url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }

            # Make the API call
            logger.info(f"Capturing PayPal order: {order_id}")
            response = requests.post(
                url,
                headers=headers,
                json={},  # Empty body for capture
                timeout=30
            )

            logger.info(f"PayPal capture response status: {response.status_code}")

            if response.status_code in (200, 201):
                capture_data = response.json()
                logger.info(f"PayPal payment captured successfully: {capture_data['id']}")
                return capture_data
            else:
                error_msg = f"Failed to capture PayPal payment: Status {response.status_code}"
                try:
                    error_details = response.json()
                    error_msg += f", Details: {json.dumps(error_details)}"
                except:
                    error_msg += f", Response: {response.text}"

                logger.error(error_msg)
                raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error when capturing PayPal payment: {str(e)}")
            raise

    def create_order_api(self, order_data):
        """
        Create a PayPal order using the Orders API directly.

        Args:
            order_data (dict): Order data to send to PayPal

        Returns:
            dict: PayPal order response
        """
        # Get access token
        access_token = self.get_access_token()
        url = f"{self.base_url}/v2/checkout/orders"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        try:
            # Make the API call
            logger.info(f"Creating PayPal order with data: {json.dumps(order_data)}")
            response = requests.post(
                url,
                headers=headers,
                json=order_data,
                timeout=30
            )

            logger.info(f"PayPal create order response status: {response.status_code}")

            if response.status_code in (200, 201):
                order_data = response.json()
                logger.info(f"PayPal order created successfully: {order_data['id']}")
                return order_data
            else:
                error_msg = f"Failed to create PayPal order: Status {response.status_code}"
                try:
                    error_details = response.json()
                    error_msg += f", Details: {json.dumps(error_details)}"
                except:
                    error_msg += f", Response: {response.text}"

                logger.error(error_msg)
                raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error when creating PayPal order: {str(e)}")
            raise

    def get_order_details(self, order_id):
        """
        Get details of a PayPal order.
        """
        # Test mode handling
        if self.test_mode:
            logger.info(f"Using test mode - simulating order details for {order_id}")
            return {
                "id": order_id,
                "status": "COMPLETED",
                "purchase_units": [
                    {
                        "reference_id": "booking_test",
                        "amount": {
                            "value": "100.00",
                            "currency_code": "USD"
                        }
                    }
                ]
            }

        try:
            # Get access token
            access_token = self.get_access_token()
            url = f"{self.base_url}/v2/checkout/orders/{order_id}"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }

            # Make the API call
            logger.info(f"Getting PayPal order details: {order_id}")
            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )

            logger.info(f"PayPal get order details response status: {response.status_code}")

            if response.status_code == 200:
                order_data = response.json()
                logger.info(f"PayPal order details retrieved successfully: {order_id}")
                return order_data
            else:
                error_msg = f"Failed to get PayPal order details: Status {response.status_code}"
                try:
                    error_details = response.json()
                    error_msg += f", Details: {json.dumps(error_details)}"
                except:
                    error_msg += f", Response: {response.text}"

                logger.error(error_msg)
                raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error when getting PayPal order details: {str(e)}")
            raise
