/* Feedback widget handler — works with Material's built-in feedback form.
   Currently logs to console. Wire up to an endpoint when ready. */
document$.subscribe(function () {
  var feedback = document.forms.feedback
  if (typeof feedback === "undefined") return

  feedback.hidden = false

  feedback.addEventListener("submit", function (ev) {
    ev.preventDefault()

    var page = document.location.pathname
    var data = ev.submitter.getAttribute("data-md-value")

    /* Log feedback (replace with fetch() to your endpoint) */
    console.log("[feedback]", { page: page, rating: data })

    feedback.firstElementChild.disabled = true

    var note = feedback.querySelector(
      ".md-feedback__note [data-md-value='" + data + "']"
    )
    if (note) note.hidden = false
  })
})
