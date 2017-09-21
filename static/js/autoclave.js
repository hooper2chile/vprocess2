$(document).ready(function() {

    namespace = '/biocl';

    // Connect to the Socket.IO server.
    var socket = io.connect(location.protocol + '//' +
	    		       document.domain + ':' +
		             location.port + namespace);


    //Se escuchan las mediciones de ph, OD, Temp.
    socket.on('Medidas', function(msg) {
        $('#med1').text('Ph: '    + msg.data[0]          ).html();
        $('#med2').text('OD: '    + msg.data[1] + ' %'   ).html();
        $('#med3').text('Temp: '  + msg.data[2] + ' º[C]').html();
    });



    //se emiten los setpoints hacia el servidor
    $('form#ac_setpoints').submit(function(event) {
        socket.emit('ac_setpoints',
                    { ac_temp: $('#temp').val(),
                      ac_time: $('#time').val(),
                      temp_en: $('#temp_enable').is(':checked'),
                      time_en: $('#time_enable').is(':checked')
                     });

        //para depurar
        console.log('Emitiendo Valores: temp, timer, good checked: ');
        console.log($('#temp').val());
        console.log($('#time').val());
	      console.log($('#time_enable').is(':checked'));
	      console.log($('#temp_enable').is(':checked'));
        return false;
    });
    //se escuchan desde el servidor los setpoints aplicados
    //para ser desplegados en todos los clientes.
    socket.on('ac_setpoints', function(msg) {
        document.getElementById('temp').value   = msg.set[0];
        document.getElementById('time').value   = msg.set[1];
        document.getElementById('temp_enable').checked = msg.set[2];
	      document.getElementById('time_enable').checked = msg.set[3];
        document.getElementById('time_set').value = msg.set[4];
        document.getElementById('temp_set').value = msg.set[5];
        //para depurar
        console.log('Checkeds Recibidos');
        console.log($('#temp').val());
        console.log($('#time').val());
	      console.log($('#time_enable').is(':checked'));
	      console.log($('#temp_enable').is(':checked'));
        console.log('probando:');
        console.log(msg.set[4]);
        console.log(msg.set[5]);
        console.log('probando2');
        console.log(msg.time_save);
        console.log(msg.temp_save);
    });




    //se emiten señal de reinicio, apagado, grabacion y limpiaza hacia el servidor
    $('form#process').submit(function(event) {
        socket.emit('power',
                    { action  : $('select[name=selection]').val(),
                      checked : $('#confirm').is(':checked')
                    });
        //para depurar
        console.log('Emitiendo Valores de Acción');
        console.log($('select[name=selection]').val())
        console.log($('#confirm').is(':checked'));

        return false;
    });

    //se escuchan desde el servidor señal de reinicio,apagado, grabacion y limpiaza
    //para ser desplegados en todos los clientes.
    socket.on('power', function(msg) {
        document.getElementById("select").value = msg.set[0]
        document.getElementById('confirm').checked = msg.set[1]

        console.log('Recibiendo Valores de Acción');
        console.log(msg.set[0]);
        console.log(msg.set[1]);
    });
});