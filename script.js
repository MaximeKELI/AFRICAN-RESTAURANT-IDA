$(function () {
    $(".hamburger-menu").on("click", function () {
      $(".toggle").toggleClass("open");
      $(".nav-list").toggleClass("open");
    });
  
    //Animation on Scroll library(AOS)
    AOS.init({
      easing: "ease",
      duration: 1000,
    });
  
    // Creating a datetimepicker
  
    $("#datetimepicker").datetimepicker({
      // format: 'YYYY/MM/DD'
      debug: true,
      icons: {
        time: "far fa-clock",
        date: "fa fa-calendar",
        dateformat: "DD / MM / YYYY",
        up: "fas fa-arrow-up",
        down: "fas fa-arrow-down",
        previous: "fas fa-chevron-left",
        next: "fas fa-chevron-right",
        today: "far fa-calendar-check-o",
        clear: "far fa-trash",
        close: "fa fa-times",
      },
      locale: "en",
      allowInputToggle: true,
      minDate: moment(),
      stepping: 15,
      showClose: true,
    });
  });
  
  //--------------Web Interaction (( Vanilla Javascript))-------------------------
  //Variables
  const meals = document.querySelector("#menu-list"),
    trayContent = document.querySelector("#tray-content tbody"),
    clearTrayButton = document.querySelector("#clear-tray");
  
  //Event Listeners
  loadEventListeners();
  
  function loadEventListeners() {
    meals.addEventListener("click", buyMeal);
  
    //remove meal whem youi tap on x
    trayContent.addEventListener("click", removeMeal);
  
    //clear Tray Button
    clearTrayButton.addEventListener("click", clearTray);
  
    // This event listener works when the dom is loaded and gets info from the local storage
    document.addEventListener("DOMContentLoaded", getFromLocalStorage);
  }
  
  //Functions
  function buyMeal(e) {
    e.preventDefault();
    //console.log(e.target.classList);
    if (e.target.classList.contains("add-to-tray")) {
      const meal = e.target.parentElement.parentElement; //get parent element
  
      getMealInfo(meal);
    }
  }
  
  function getMealInfo(meal) {
    const mealInfo = {
      title: meal.querySelector("h1").textContent,
      price: meal.querySelector("h6").textContent,
      image: meal.previousElementSibling.querySelector("img").src,
      id: meal.querySelector("#add-to-tray").getAttribute("data-id"),
    };
  
    // console.log(mealInfo);
  
    addIntoTray(mealInfo);
  }
  
  function addIntoTray(meal) {
    //Create the html to be used in the table to replace the empty spaces
  
    row = document.createElement("tr");
  
    row.innerHTML = `
    <tr>
      <td>
        <img src= "${meal.image}" width=70 height=50>
      </td>
      <td style="fontsize:10px">${meal.title}</td>
      <td>${meal.price}</td>
      <td>
        <a href="#" class="remove" data-id= "${meal.id}">X</a> 
      </td>
    </tr>
    `;
  
    trayContent.append(row);
  
    //Local storage
    saveIntoStorage(meal);
  }
  
  function saveIntoStorage(meal) {
    let meals = getMealsFromStorage();
  
    meals.push(meal);
  
    // console.log(meals);
    localStorage.setItem("meals", JSON.stringify(meals));
  }
  
  function getMealsFromStorage() {
    let meals;
    //If something exist on storage, get the value, otherwise create an empty array
    if (localStorage.getItem("meals") === null) {
      meals = [];
    } else {
      //Parse converts from string to object
      meals = JSON.parse(localStorage.getItem("meals"));
    }
  
    return meals;
  }
  
  function removeMeal(e) {
    let meal, mealId;
    if (e.target.classList.contains("remove")) {
      e.target.parentElement.parentElement.remove();
      meal = e.target.parentElement.parentElement;
      mealId = meal.querySelector("a").getAttribute("data-id");
    }
  
    // console.log(courseId);
    // Remove from the local stroage
    removeMealLocalStorage(mealId);
  
    // console.log(meal);
  }
  
  function removeMealLocalStorage(id) {
    // get the local storage data
    let mealsLS = getMealsFromStorage();
  
    // Loop through the array and find the index to remove
    mealsLS.forEach(function (mealLS, index) {
      if (mealLS.id === id) {
        mealsLS.splice(index, 1);
      }
    });
  
    //Add the rest of the array
    localStorage.setItem("meals", JSON.stringify(mealsLS));
  
    // console.log(mealsLS);
  }
  
  function clearTray(e) {
    // trayContent.remove();
    // trayContent.innerHTML = "",
  
    //Preffered way to use it
    while (trayContent.firstChild) {
      trayContent.removeChild(trayContent.firstChild);
    }
    clearLocalStorage();
  }
  
  // Clear from the whole local strorage
  function clearLocalStorage() {
    localStorage.clear();
  }
  
  function getFromLocalStorage() {
    let mealsLS = getMealsFromStorage();
  
    // Loop through the meals and add into tray
    mealsLS.forEach(function (meal) {
      //create the <tr>
  
      const row = document.createElement("tr");
  
      row.innerHTML = `
      <tr>
        <td>
          <img src="${meal.image}" width=70 height=50>
        </td>
        <td>${meal.title}</td>
        <td>${meal.price}</td>
        <td>
          <a href="#" class= "remove" data-id = "${meal.id}"> X </a>
        </td>
      </tr>
      `;
      trayContent.appendChild(row);
    });
  }