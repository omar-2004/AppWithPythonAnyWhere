var UserFound = false;
var inputYear = document.getElementById("InputYear");
inputYear.addEventListener("blur", function () {
  if (inputYear.value != "Year") {
    if (!UserFound) {
      alert("Error: Error not found.");
      return false;
    }
    fetch("/api/data/GetYearAndInformation", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ inputYear: inputYear.value }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          resetAll(0);
          var months = [
            "01. January",
            "02. February",
            "03. March",
            "04. April",
            "05. May",
            "06. June",
            "07. July",
            "08. August",
            "09. September",
            "10. October",
            "11. November",
            "12. December",
          ];

          var tableBody = document.getElementById("Table");
          for (var i = 0; i < data.myresult.length; i++) {
            var row = document.createElement("tr");
            var monthCell = document.createElement("td");
            monthCell.textContent = months[Number(data.myresult[i][0]) - 1];
            row.appendChild(monthCell);

            var randomNumberCell = document.createElement("td");
            randomNumberCell.textContent = data.myresult[i][1];
            row.appendChild(randomNumberCell);

            var viewCell = document.createElement("td");
            viewCell.innerHTML =
              "<a href=/viewMonth/" +
              String(Number(data.myresult[i][0])) +
              ">View</a>";
            row.appendChild(viewCell);
            if (i == 0) {
              var viewAll = document.createElement("td");
              viewAll.colSpan = 12;
              viewAll.innerHTML =
                "<a href=/viewYear/" + inputYear.value + ">View</a>";
              row.appendChild(viewAll);
            }
            tableBody.appendChild(row);
          }
        } else {
          resetAll(0);
        }
      })
      .catch((error) => {
        alert("Error: Unauthorized access");
      });
  }
});

function resetAll(DeleteALL = true) {
  if (DeleteALL) {
    GivingUserID = document.getElementById("UserID");
    GivingUserFisrtName = document.getElementById("firstName");
    GivingUserLastName = document.getElementById("lastName");
    document.getElementById("InputYear").disabled = true;
    document.getElementById("InputYear").selected = 0;
    GivingUserID.disabled = false;
    GivingUserFisrtName.disabled = false;
    GivingUserLastName.disabled = false;
    GivingUserID.value = "";
    GivingUserFisrtName.value = "";
    GivingUserLastName.value = "";
    UserFound = false;
  }
  var tableBody = document.getElementById("Table");
  if (tableBody) {
    while (tableBody.firstChild) {
      tableBody.removeChild(tableBody.firstChild);
    }
  }
}

function FNAddUpdateValueToTheDataBase() {
  const inputYear = document.getElementById("date").value;
  const dataToSend = {
    inputYear: inputYear,
  };
  fetch("/api/data/GetYearAndInformation", {
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
      alert("Error: Unauthorized access");
    });
}

function GetTheUserFromDataBase() {
  GivingUserID = document.getElementById("UserID");
  GivingUserFisrtName = document.getElementById("firstName");
  GivingUserLastName = document.getElementById("lastName");
  const dataToSend = {
    GivingUserID: GivingUserID.value,
    GivingUserFisrtName: GivingUserFisrtName.value,
    GivingUserLastName: GivingUserLastName.value,
  };
  fetch("/api/data/GetTheUserFromDataBase", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(dataToSend),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      }
      throw new Error("User not found");
    })
    .then((data) => {
      if (data.success) {
        UserFound = true;
        GivingUserID.disabled = true;
        GivingUserFisrtName.disabled = true;
        GivingUserLastName.disabled = true;
        GivingUserID.value = data.GuestID;
        GivingUserFisrtName.value = data.GuestFirstName;
        GivingUserLastName.value = data.GuestLastName;
        document.getElementById("InputYear").disabled = false;
        alert("User found");
      } else {
        resetAll(1);
      }
    })
    .catch((error) => {
      alert("Error: User not found!");
    });
}
