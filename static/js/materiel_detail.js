$('body').on('click','.show',function(e){
    var data = $(e.target).text()
    if(data.split('')[0]=='+'){
        $(e.target).text(data.replace('+','-'))

    }else{
            $(e.target).text(data.replace('-','+'))
    }
    $(e.target).next('div').toggle()
})

$('body').on('click','#deplier', function(){
    var datas = $('.show')
    var long = datas.length

    if($(this).text()=='Replier tout'){
        $(this).text('Déplier tout');
        $('.show').next('div').hide();
        for(var i=0; i<datas.length; i++){
           var data = (datas[i].innerText).replace('-','+')
           datas[i].innerText = data
        }

    }else{
        $(this).text('Replier tout');
        $('.show').next('div').show();
        for(var i=0; i<datas.length; i++){
           var data = (datas[i].innerText).replace('+','-')
           datas[i].innerText = data
        }
    }

})