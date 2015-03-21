$ ->
  if $('.toc').length
    $('.page-wrapper :header').waypoint
      offset: '10px'
      handler: (direction) ->
        _id = $(@).attr('id')
        if _id and $("[href=##{_id}]").length
          $(".toc [href]").removeClass 'active'
          $("[href=##{_id}]").addClass 'active'
    $('.toc').addClass('hidden-md hidden-sm hidden-xs')

  # Fix image in page content
  $('.page-content img').parent().addClass('text-center')
  $("[data-toggle='tooltip']").tooltip()