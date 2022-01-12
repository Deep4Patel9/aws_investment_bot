### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


### Validate Inputs ###
def validate_age(age, intent_request):
    """
    Validates the age provided by the user.
    """

    # Validate the age, it should be > 0 and < 65
    if age is not None:
        age = parse_int(
            age
        )  # Since parameters are strings it's important to cast values
        if age <= 0 or age >= 65:
            return build_validation_result(
                False,
                "age",
                "The age should be greater than zero and less than 65, "
                "Please provide the correct age.",
            )

    # A True results is returned if age or amount are valid
    return build_validation_result(True, None, None)
    
    
def validate_investment_amount(investment_amount, intent_request):
    """
    Validates the investment_amount provided by the user.
    """

    # Validate the investment_amount should be equal to or greater than 5000.
    if investment_amount is not None:
        investment_amount = parse_int(
            investment_amount
        )  # Since parameters are strings it's important to cast values
        if investment_amount < 5000:
            return build_validation_result(
                False,
                "investmentAmount",
                "The investmentAmount should be greater than or equal to 5000, "
                "Please provide a correct investmentAmount in dollars.",
            )

    # A True results is returned if age or amount are valid
    return build_validation_result(True, None, None)


def validate_risk_level(risk_level, intent_request):
    """
    Validates the riskLevel provided by the user.
    """

    # Validate the risk_level should be 'low', 'medium', 'high', 'none'.
    if risk_level is not None:
        if risk_level.lower() not in ['low', 'medium', 'high', 'none']:
            return build_validation_result(
                False,
                "riskLevel",
                "The riskLevel should be of the following: none, low, medium, high, "
                "Please provide a valid Risk Level.",
            )

    # A True results is returned if age or amount are valid
    return build_validation_result(True, None, None)


def risk_recommend(risk_level, intent_request):
    risk_level = risk_level.lower()
    if risk_level == 'low':
        return "60% bonds (AGG), 40% equities (SPY)"
    elif risk_level == 'medium':
        return "40% bonds (AGG), 60% equities (SPY)"
    elif risk_level == 'high':
        return "20% bonds (AGG), 80% equities (SPY)"
    elif risk_level == 'none': 
        return "100% bonds (AGG), 0% equities (SPY)"

    

### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # This code performs basic validation on the supplied input slots.

        # Gets all the slots
        slots = get_slots(intent_request)

        # Validates user's input using the validation functions
        age_valid = validate_age(age, intent_request)

        # If the data provided by the user is not valid,
        # the elicitSlot dialog action is used to re-prompt for the first violation detected.
        if not age_valid["isValid"]:
            slots[age_valid["violatedSlot"]] = None  # Cleans invalid slot

            # Returns an elicitSlot dialog to request new data for the invalid slot
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                age_valid["violatedSlot"],
                age_valid["message"],
            )

        # Fetch current session attributes
        output_session_attributes = intent_request["sessionAttributes"]
        
        invest_amount_valid = validate_investment_amount(investment_amount, intent_request)
       
        if not invest_amount_valid["isValid"]:
            slots[invest_amount_valid["violatedSlot"]] = None  # Cleans invalid slot

            # Returns an elicitSlot dialog to request new data for the invalid slot
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                invest_amount_valid["violatedSlot"],
                invest_amount_valid["message"],
            )

        # Fetch current session attributes
        output_session_attributes = intent_request["sessionAttributes"]

        risk_level_valid = validate_risk_level(risk_level, intent_request)

        if not risk_level_valid["isValid"]:
            slots[risk_level_valid["violatedSlot"]] = None  # Cleans invalid slot

            # Returns an elicitSlot dialog to request new data for the invalid slot
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                risk_level_valid["violatedSlot"],
                risk_level_valid["message"],
            )

        # Fetch current session attributes
        output_session_attributes = intent_request["sessionAttributes"]

        # Once all slots are valid, a delegate dialog is returned to Lex to choose the next course of action.
        return delegate(output_session_attributes, get_slots(intent_request))

    # Get recommended portfolio based on riskLevel user input
    port_rec = risk_recommend(risk_level, intent_request)
    
    
    # Return a message with portfolio recommendation result.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """Thank you for your information.;
            Based on your risk level of {}, the portfolio setup recommended for you is {}.
            """.format(
                risk_level, port_rec
            ),
        },
    )
    


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "recommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)