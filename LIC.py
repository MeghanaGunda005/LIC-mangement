from flask import Flask, render_template,redirect,request
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["lic"]
collection = db["data"]

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/list')
def display_table():
    data = list(collection.find({}, {"_id": 0}))
    return render_template("List.html", data=data)

@app.route("/display", methods=["GET", "POST"])
def display():
    result = None
    if request.method == "POST":
        policy_no = request.form.get("policyNo")
        result = collection.find_one({"Policy No": int(policy_no)}, {"_id": 0})
    return render_template("Display.html", data=result)

def safe_int(value):
    try:
        return int(value) if value is not None and value.strip() != "" else None
    except ValueError:
        return None

@app.route("/edit", methods=["GET", "POST"])
def edit():
    data = None

    if request.method == "POST":
        if "update" in request.form:
            # User clicked "Update"
            policy_no = safe_int(request.form.get("Policy No"))
            updated_data = {
                "Cell No": safe_int(request.form.get("Cell No")),
                "DOB": request.form.get("DOB"),
                "Policy No": policy_no,
                "Name": request.form.get("Name"),
                "SA": request.form.get("SA"),
                "Plan No": safe_int(request.form.get("Plan No")),
                "DOC": request.form.get("DOC"),
                "Term": safe_int(request.form.get("Term")),
                "PPT": safe_int(request.form.get("PPT")),
                "DOM": request.form.get("DOM"),
                "Premium": safe_int(request.form.get("Premium")),
                "Mode": request.form.get("Mode"),
                "Next Due": request.form.get("Next Due")
            }
            collection.update_one({"Policy No": policy_no}, {"$set": updated_data})
            data = updated_data  # Show updated data again

        else:
            # User submitted policy number to search
            policy_no = safe_int(request.form.get("policyNo"))
            if policy_no:
                data = collection.find_one({"Policy No": policy_no}, {"_id": 0})
            else:
                data = None

    return render_template("Edit.html", data=data)

@app.route("/new", methods=["GET", "POST"])
def new():
    message = ''
    if request.method == 'POST':
        policy_data = {
            'Cell No': request.form.get('Cell No'),
            'DOB': request.form.get('DOB'),
            'Policy No': int(request.form.get('Policy No')) if request.form.get('Policy No') else None,
            'Name': request.form.get('Name'),
            'SA': request.form.get('SA'),
            'Plan No': request.form.get('Plan No'),
            'DOC': request.form.get('DOC'),
            'Term': int(request.form.get('Term')) if request.form.get('Term') else None,
            'PPT': int(request.form.get('PPT')) if request.form.get('PPT') else None,
            'DOM': request.form.get('DOM'),
            'Premium': request.form.get('Premium'),
            'Mode': request.form.get('Mode'),
            'Next Due': request.form.get('Next Due'),
            'Status' : request.form.get('Status'),
        }
        collection.insert_one(policy_data)
        message = 'New policy entry inserted successfully!'

    return render_template("New.html", message=message)

@app.route("/close", methods=["GET", "POST"])
def close_policy():
    if request.method == "POST":
        policy_no = request.form.get("policy_no")
        result = collection.update_one(
            {"policy_no": policy_no},
            {"$set": {"Status": "Closed"}}
        )

        if result.matched_count > 0:
            return f"<h2>Policy has been successfully closed.</h2><a href='/'>Back to Home</a>"
        else:
            return f"<h2>Policy not found.</h2><a href='/close'>Try Again</a>"

    return render_template("Close.html")



if __name__ == '__main__':
    app.run(debug=True)
