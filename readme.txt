< Comandos para inicializar el software clinico >

Existe migraciones para Celery Beat
python manage.py migrate django_celery_beat

Celery Beat
celery -A doctor beat -l info

Worker
celery -A doctor worker -l info --pool=solo

Django Run Server
py manage.py runserver


{% block js %}
<script>
    class AtencionMedica {
        constructor(detalleUpdate) {
            this.paciente = '';
            this.peso = '';
            this.altura = '';
            this.presionArterial = '';
            this.pulso = '';
            this.temperatura = '';
            this.saturacionOxigeno = '';
            this.frecuenciaRespiratoria = '';
            this.motivoConsulta = '';
            this.sintomas = '';
            this.examenFisico = '';
            this.tratamiento = '';
            this.examenesEnviados = '';
            this.comentarioAdicional = '';
            this.diagnostico = [];
            this.medicamentos = [];

            if (detalleUpdate && detalleUpdate.length > 0) {
                detalleUpdate.forEach(det => {
                    let codigo = det.medicamento_id;
                    let nombre = det.medicamento__nombre;
                    let cantidad = det.cantidad;
                    let prescripcion = det.prescripcion;
                    console.log(codigo, nombre, cantidad, prescripcion);
                    this.medicamentos.push({codigo, nombre, cantidad, prescripcion});
                });
                this.syncTable();
            }
        }

        addMedication(codigo, nombre, cantidad, prescripcion) {
            const existingMedication = this.medicamentos.findIndex(med => med.codigo === codigo);
            cantidad = (cantidad.trim() === "") ? 0 : parseInt(cantidad);
            if (existingMedication >= 0) {
                alert('Este medicamento ya está en la lista. Actualizando cantidad y prescripción.');
                this.medicamentos[existingMedication].cantidad += cantidad;
                this.medicamentos[existingMedication].prescripcion = prescripcion;
            } else {
                this.medicamentos.push({codigo, nombre, cantidad, prescripcion});
            }
            this.syncTable();
        }

        removeMedication(codigo) {
            this.medicamentos = this.medicamentos.filter(med => med.codigo !== codigo);
            this.syncTable();
        }

        syncTable() {
            const tableBody = document.querySelector('#medicationsTable tbody');
            tableBody.innerHTML = '';
            this.medicamentos.forEach((med, index) => {
                const row = `
                    <tr>
                        <td>${med.codigo}</td>
                        <td>${med.nombre}</td>
                        <td>${med.cantidad}</td>
                        <td>${med.prescripcion}</td>
                        <td>
                            <button class="btn btn-danger" onclick="atencionMedica.removeMedication('${med.codigo}')">
                                <i class="fas fa-trash"></i> Eliminar
                            </button>
                        </td>
                    </tr>`;
                tableBody.innerHTML += row;
            });
        }

        saveAtencion() {
            this.paciente = document.querySelector('#id_paciente').value;
            this.peso = document.querySelector('#id_peso').value;
            this.altura = document.querySelector('#id_altura').value;
            this.presionArterial = document.querySelector('#id_presion_arterial').value;
            this.pulso = document.querySelector('#id_pulso').value;
            this.temperatura = document.querySelector('#id_temperatura').value;
            this.saturacionOxigeno = document.querySelector('#id_saturacion_oxigeno').value;
            this.frecuenciaRespiratoria = document.querySelector('#id_frecuencia_respiratoria').value;
            this.motivoConsulta = document.querySelector('#id_motivo_consulta').value;
            this.sintomas = document.querySelector('#id_sintomas').value;
            this.examenFisico = document.querySelector('#id_examen_fisico').value;
            this.tratamiento = document.querySelector('#id_tratamiento').value;
            this.examenesEnviados = document.querySelector('#id_examenes_enviados').value;
            this.comentarioAdicional = document.querySelector('#id_comentario_adicional').value;

            this.diagnostico = Array.from(document.getElementById("id_diagnostico").selectedOptions).map(option => option.value);

            if (!this.paciente || !this.peso || !this.altura || !this.presionArterial || !this.pulso ||
                !this.temperatura || !this.saturacionOxigeno || !this.frecuenciaRespiratoria ||
                !this.motivoConsulta || !this.sintomas || !this.examenFisico || !this.diagnostico ||
                !this.tratamiento || !this.examenesEnviados) {
                alert('Por favor, complete todos los campos obligatorios.');
                return;
            }

            if (!this.medicamentos.length) {
                alert('Por favor, agregue al menos un medicamento.');
                return;
            }

            const data = {
                paciente: this.paciente,
                peso: this.peso,
                altura: this.altura,
                presionArterial: this.presionArterial,
                pulso: this.pulso,
                temperatura: this.temperatura,
                saturacionOxigeno: this.saturacionOxigeno,
                frecuenciaRespiratoria: this.frecuenciaRespiratoria,
                motivoConsulta: this.motivoConsulta,
                sintomas: this.sintomas,
                examenFisico: this.examenFisico,
                diagnostico: this.diagnostico,
                tratamiento: this.tratamiento,
                examenesEnviados: this.examenesEnviados,
                comentarioAdicional: this.comentarioAdicional,
                medicamentos: this.medicamentos
            };
            console.log(data);

            const url = window.location.pathname.trim();
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                alert(data.msg);
                window.location.href = '/attention_list/';
            })
            .catch(error => {
                console.error('Error al guardar la atención médica:', error);
            });
        }
    }

    const detailAtencionUpdate = JSON.parse('{{ detail_atencion|safe }}');
    const atencionMedica = new AtencionMedica(detailAtencionUpdate);

    function addMedication() {
        const codigo = document.querySelector('#medicationSelect').value;
        const nombre = document.querySelector('#medicationSelect option:checked').text;
        const cantidad = document.querySelector('#medicationQuantity').value;
        const prescripcion = document.querySelector('#medicationPrescription').value;
        atencionMedica.addMedication(codigo, nombre, cantidad, prescripcion);
    }
</script>
{% endblock %}
