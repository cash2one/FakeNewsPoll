function vote (id, opinion) {
  $.ajax({
    url: "/vote/",
    type: "post",
    contentType: "application/json",
    dataType: "json",
    data: JSON.stringify({"id": id, "opinion": opinion}),
    success: function () {
      console.log("Succes!");
    }
  });
}
