function OnLoad() {
  let navItemList = document.getElementsByClassName("nav-item"); // take all elements nav item
  for(i=0;i<navItemList.length;i++) // i++ == i=i+1
  {
      let hrefElement = navItemList[i].children[0]  // take first element of nav item, ie a href url
      if(window.location.href == hrefElement.href)  // if window url = nav item url
                                                    // if window url contains dictionary key, if key value of  = nav item url
      {
          hrefElement.classList.remove("nav-link");
          hrefElement.classList.add("active");
      }
      else
      {
        if((window.location.href.includes("profil_editace") || window.location.href.includes("sluzby")) && hrefElement.href.includes("profil"))
        {
          hrefElement.classList.remove("nav-link");
          hrefElement.classList.add("active");
        }
        else if((window.location.href.includes("match") || window.location.href.includes("email_sent")) && hrefElement.href.includes("prehled_all"))
        {
          hrefElement.classList.remove("nav-link");
          hrefElement.classList.add("active");
        }
        else if(window.location.href.includes("requests_detail") && hrefElement.href.includes("requests"))
        {
          hrefElement.classList.remove("nav-link");
          hrefElement.classList.add("active");
        }
        else
        {
          hrefElement.classList.remove("active");
          hrefElement.classList.add("nav-link");
        }
      }

  }
  //popover initialize
    $(function () {
      $('[data-toggle="popover"]').popover()
    })
  


}

window.onload = OnLoad;