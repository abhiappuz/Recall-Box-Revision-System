import requests

BASE_URL = "http://127.0.0.1:8000/api/revision/"


def start_revision_session(user_id, topic_id, session_mode):

    url = BASE_URL + "start-session/"

    data = {
        "user_id": user_id,
        "topic_id": topic_id,
        "status": "IN_PROGRESS",
        "session_mode": session_mode
    }

    try:
        response = requests.post(url, json=data, timeout=10)

        if response.status_code == 201:
            return response.json()

        try:
            return {"error": response.json()}
        except ValueError:
            return {"error": response.text}

    except requests.RequestException as error:
        return {"error": str(error)}


def save_questions(questions, bank_id):

    url = BASE_URL + "save-questions/"

    data = {
        "bank_id": bank_id,
        "questions": questions
    }

    try:
        response = requests.post(
            url,
            json=data,
            timeout=10
        )

        if response.status_code == 201:
            return response.json()

        try:
            return {"error": response.json()}
        except ValueError:
            return {"error": response.text}

    except requests.RequestException as error:
        return {"error": str(error)}


def create_question_bank(topic_id, bank_name):

    url = BASE_URL + "create-bank/"

    data = {
        "topic_id": topic_id,
        "bank_name": bank_name
    }

    try:
        response = requests.post(
            url,
            json=data,
            timeout=10
        )

        if response.status_code == 201:
            return response.json()

        try:
            return {"error": response.json()}
        except ValueError:
            return {"error": response.text}

    except requests.RequestException as error:
        return {"error": str(error)}

def get_question_banks(topic_id):

    url = BASE_URL + "get-banks/"

    params = {
        "topic_id": topic_id
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        try:
            return {"error": response.json()}
        except ValueError:
            return {"error": response.text}

    except requests.RequestException as error:
        return {"error": str(error)}

    
def get_questions(topic_id):

    url = BASE_URL + "get-questions/"

    params = {
        "topic_id": topic_id
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        try:
            return {"error": response.json()}
        except ValueError:
            return {"error": response.text}

    except requests.RequestException as error:
        return {"error": str(error)}

def save_answer_attempt(user_id, session_id, question_id, selected_answer, time_taken):

    url = BASE_URL + "save-answer/"

    data = {
        "user_id": user_id,
        "session": session_id,
        "question": question_id,
        "selected_answer": selected_answer,
        "time_taken": time_taken
    }

    try:
        response = requests.post(
            url,
            json=data,
            timeout=10
        )

        if response.status_code == 201:
            return response.json()

        try:
            return {"error": response.json()}
        except ValueError:
            return {"error": response.text}

    except requests.RequestException as error:
        return {"error": str(error)}


def complete_revision_session(session_id):
    url = BASE_URL + "complete-session/"

    data = {
        "session_id": session_id
    }

    try:
        response = requests.post(url, json=data, timeout=10)

        if response.status_code == 200:
            return response.json()

        try:
            return {"error": response.json()}
        except ValueError:
            return {"error": response.text}

    except requests.RequestException as error:
        return {"error": str(error)}
    


# ---------------- SUBJECT AND TOPIC APIs ----------------

def add_revision_topic(user_id, subject_name, topic_name):

    url = BASE_URL + "add-topic/"

    data = {
        "user_id": user_id,
        "subject_name": subject_name,
        "topic_name": topic_name
    }

    try:
        response = requests.post(url, json=data, timeout=10)

        if response.status_code == 201:
            return response.json()

        return {"error": response.json()}

    except requests.RequestException as error:
        return {"error": str(error)}


def get_revision_subjects(user_id):

    url = BASE_URL + "get-subjects/"

    try:
        response = requests.get(
            url,
            params={"user_id": user_id},
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        return {"error": response.json()}

    except requests.RequestException as error:
        return {"error": str(error)}


def get_revision_topics(user_id, subject_name):

    url = BASE_URL + "get-topics/"

    params = {
        "user_id": user_id,
        "subject_name": subject_name
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        return {"error": response.json()}

    except requests.RequestException as error:
        return {"error": str(error)}


def delete_revision_topic(topic_id):

    url = BASE_URL + f"delete-topic/{topic_id}/"

    try:
        response = requests.delete(url, timeout=10)

        if response.status_code == 200:
            return response.json()

        return {"error": response.json()}

    except requests.RequestException as error:
        return {"error": str(error)}


def get_bank_questions(bank_id):

    url = BASE_URL + "get-bank-questions/"

    try:
        response = requests.get(
            url,
            params={"bank_id": bank_id},
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        try:
            return {"error": response.json()}
        except ValueError:
            return {"error": response.text}

    except requests.RequestException as error:
        return {"error": str(error)}


def update_question(question_id, data):

    url = BASE_URL + f"update-question/{question_id}/"

    try:
        response = requests.put(
            url,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        try:
            return {"error": response.json()}
        except ValueError:
            return {"error": response.text}

    except requests.RequestException as error:
        return {"error": str(error)}