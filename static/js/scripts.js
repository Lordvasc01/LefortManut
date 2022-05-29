/*!
* Start Bootstrap - Bare v5.0.0 (https://startbootstrap.com/template/bare)
* Copyright 2013-2021 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-bare/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project
$(document).ready(function(){
    $('body').on('click', '#content', function(){
        $('#resultat').hide()
        $('#search').val('')
    })
    $('body').on('click','#resultat-text', function(){
        console.log($(this).text())
    })


    $('body').on('keyup','#search',function(e){
        if (e.target.value.length>1){
            $('#resultat').show()
            $('#resultat-text').text(e.target.value)

        }else{

            $('#resultat').hide()
        }
        
    })

    // navigation spa
    $('bodyz').on('click','a',function(e){
        e.preventDefault()
        var href = e.target.href
        var xml = new XMLHttpRequest()
        xml.responseType = 'document'
        xml.open('get',href+'#content', 'true')
        xml.onload = function(){
            
            document.getElementById('content').innerHTML = this.response.getElementById('content').innerHTML;
        }
        xml.send()
        //$('#content').load( href + ' #content');
    })

  // datepicker
  $.datetimepicker.setLocale('fr');
  $('#date_debut').datetimepicker(
  {
    format: 'd-m-Y h:i',
    });

  // cloture ordre de maintenance
    $('#date_cloture').datetimepicker(
  {
    format: 'd-m-Y h:i',
    });

    $('#heure_debut').datetimepicker(
  {
    format: 'd-m-Y h:i',

    });

    $('#heure_fin').datetimepicker(
  {
    format: 'd-m-Y h:i',
    });

      $('#date_intervention').datetimepicker(
  {
    format: 'd-m-Y',
    timepicker:false,
    });


    $('#date_depart').datetimepicker(
      {
        format: 'd-m-Y',
        timepicker:false,
        });


     $('#date_fin').datetimepicker(
  {
    format: 'd-m-Y',
    timepicker:false,
    });
})



