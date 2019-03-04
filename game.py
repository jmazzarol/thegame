import json
import typing

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    raise Exception("What do you mean you don't already have requests installed?!?!")

# Note to Tim
#
# This code was written after the fact, as I thought the game was simply in the lead-up to a specific coding problem.
# I used Postman to navigate the API, and didn't save my states after each query. However since that would be boring to
# talk about I figured I would write up my algorithm so we might at least have something to discuss.
#
# "i have only proved it correct not tested it" - Don Knuth

BASE_URL = ''
USERNAME = ''

basic_auth = HTTPBasicAuth(USERNAME, "love to code")

json_headers = {"Content-Type": "application/json"}


def apply(
    preferred_name: str = "Dade Murphy", email_address: str = "zer0c00l@thegibson.net"
) -> typing.Optional[str]:
    # RETURNS Applicant ID or None
    # TODO: Add try catch around request. Check for http connection problems, non JSON responses and error cases
    r = requests.post(
        f"https://{BASE_URL}/apply",
        data=json.dumps(
            {"PreferredName": preferred_name, "EmailAddress": email_address}
        ),
        auth=basic_auth,
        headers=json_headers,
    )
    return r.json().get("ApplicantID")


def setup_game(applicant_id: str) -> typing.Optional[str]:
    # Returns GameID
    r = requests.post(
        f"https://{BASE_URL}/guess",
        auth=basic_auth,
        headers=json_headers,
        data=json.dumps({"ApplicantID": applicant_id}),
    )
    return r.json().get("GameID")


def play_game(
    applicant_id: str,
    game_id: str,
    low: int = 0,
    high: int = 100000,
    higher: bool = True,
    dt: bool = False,
) -> int:

    if high != low:
        # Not sure if this is accurate, but I believe I remember reading something on strategy arguing that guessing
        # 1/3 or 2/3 of the difference is a more optimal strategy as on worst case it is very similar to the 50%
        # strategy while allowing for "lucky guesses" to eliminate a larger segment of the search space.
        # For a real production application I would actually research, however I assume you wanted this as a "As is"
        # application.
        third = int((high - low) / 3)
        guess = low + third
        if higher is True:
            guess += third
    else:
        guess = low

    payload = {"ApplicantID": applicant_id, "GameID": game_id, "Guess": guess}
    if dt is True:
        payload["DastardlyTrick"] = False

    r = requests.put(
        f"https://{BASE_URL}/guess",
        auth=basic_auth,
        headers=json_headers,
        data=json.dumps(payload),
    )

    results = r.json()

    if results.get("Won") is True:
        return results.get("Guess")

    if results.get("DastardlyTrick"):
        return play_game(
            applicant_id=applicant_id,
            game_id=game_id,
            low=guess + 1,
            high=high,
            higher=True,
            dt=True,
        )

    # Recursion... lets see if we can guess before we blow the stack
    if results.get("HigherLower") == "Higher":
        return play_game(
            applicant_id=applicant_id,
            game_id=game_id,
            low=guess + 1,
            high=high,
            higher=True,
            dt=dt,
        )
    else:
        return play_game(
            applicant_id=applicant_id,
            game_id=game_id,
            low=low,
            high=guess - 1,
            higher=False,
            dt=dt,
        )


def go():
    app_id = apply(
        preferred_name="Thomas Anderson", email_address="neo@nebuchadnezzar.zion.org"
    )
    if app_id is None:
        raise Exception("Applicant ID not found")
    game_id = setup_game(app_id)
    if game_id is None:
        raise Exception("Game ID not found")


if __name__ == "__main__":
    pass
