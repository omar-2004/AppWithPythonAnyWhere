const inputElement = document.getElementById("date");
inputElement.addEventListener("blur", function () {
  const inputValue = inputElement.value;
  const inputDate = new Date(inputValue);
  const currentDate = new Date();
  const apiKey = "71031886606-a1f90-4afca-a306-bc05ac63d896b9b";
  if (inputDate > currentDate || inputDate == "Invalid Date") {
    alert("Error: Input date invalid please check the date.");
  } else {
    fetch("/api/data/modifyHoursAndUpdate", {
      method: "POST",
      body: JSON.stringify({ data: inputValue }),
      headers: {
        "Content-Type": "application/json",
        "Api-Key": apiKey,
      },
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        throw new Error("Unauthorized");
      })
      .then((data) => {
        if (data.success) {
          document.getElementById("nbrOfHour").value = data.numOfHours;
          document.getElementById("comments").value = data.comments;
          document.getElementById("confirmationBtn").value = "Update";
        } else {
          resetInput();
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        document.getElementById("api-data").textContent =
          "Error: Unauthorized access";
      });
  }
});

function resetInput() {
  document.getElementById("nbrOfHour").value = "";
  document.getElementById("comments").value = "";
  document.getElementById("nbrOfHour").disabled = false;
  document.getElementById("confirmationBtn").value = "Confirme";
  document.getElementById("comments").disabled = false;
}

function FNAddUpdateValueToTheDataBase() {
  var inputDate = document.getElementById("date").value;
  const inputNumberOfWorking = document.getElementById("nbrOfHour").value;
  const inputComment = document.getElementById("comments").value;
  const apiKey = "71031886606-a1f90-4afca-a306-bc05ac63d896b9s";
  const dataToSend = {
    inputDate: inputDate,
    inputNumberOfWorking: inputNumberOfWorking,
    inputComment: inputComment,
  };
  fetch("/api/data/AddAndUpdate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(dataToSend),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("Update successfully");
        document.getElementById("date").value = "";
        resetInput();
      } else {
        alert("Update failed");
      }
    })

    .catch((error) => {
      console.error("Error:", error);
      document.getElementById("api-data").textContent =
        "Error: Unauthorized access";
    });
}
