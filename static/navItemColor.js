function OnLoad() {
    let navItemList = document.getElementsByClassName("nav-item"); // take all elements nav item
    for(i=0;i<navItemList.length;i++) // i++ == i=i+1
    {
        let hrefElement = navItemList[i].children[0]  // take first element of nav item, ie a href url
        if(window.location.href == hrefElement.href)  // if window url = nav item url
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

window.onload = OnLoad;