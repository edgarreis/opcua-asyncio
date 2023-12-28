import asyncio
import logging
import numpy as np
from asyncua import Server, ua
from asyncua.common.methods import uamethod

@uamethod
def func(parent, value):
    return value * 2

def senoide_aleatoria(tempo, amplitude, frequencia, amplitude_ruido):
    componente_senoidal = amplitude * np.sin(2 * np.pi * frequencia * tempo)
    componente_ruido = amplitude_ruido * np.random.uniform(-1, 1, len(tempo))
    return componente_senoidal + componente_ruido

async def main():
    _logger = logging.getLogger(__name__)
    
    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4848/freeopcua/server/")

    # set up our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io" # Nome do Servidor #SenseIoT
    idx = await server.register_namespace(uri)

    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    myobj = await server.nodes.objects.add_object(idx, "MyObject")  # Insere um equipamento
    myvar = await myobj.add_variable(idx, "MyVariable", 6.7)        # Insere as variaveis
    myvar2 = await myobj.add_variable(idx, "MyVariable2", 0.0)
    
    # server.nodes, contains links to very common nodes like objects and root
    myobj2 = await server.nodes.objects.add_object(idx, "MyObject2")  # Insere um equipamento
    mytemp = await myobj2.add_variable(idx, "temperatura", 6.7)        # Insere as variaveis
    mypressure = await myobj2.add_variable(idx, "pressao", 0.0)

    # Set MyVariable to be writable by clients
    await myvar.set_writable()
    await myvar2.set_writable()
    await mytemp.set_writable()
    await mypressure.set_writable()
    
    await server.nodes.objects.add_method(
        ua.NodeId("ServerMethod", idx),
        ua.QualifiedName("ServerMethod", idx),
        func,
        [ua.VariantType.Int64],
        [ua.VariantType.Int64],
    )
    
    _logger.info("Starting server!")

    async with server:
        tempo_inicial = 0
        tempo_final = 10
        frequencia_amostragem = 1  # 1 ponto por segundo
        numero_pontos = int((tempo_final - tempo_inicial) * frequencia_amostragem)
        tempo = np.linspace(tempo_inicial, tempo_final, numero_pontos)

        while True:
            await asyncio.sleep(1)
            
            # Gera a forma senoidal aleatória para MyVariable2
            valor_senoide_aleatoria = senoide_aleatoria(tempo, amplitude=1.0, frequencia=1.0, amplitude_ruido=0.1)
            new_val2 = valor_senoide_aleatoria[len(valor_senoide_aleatoria) - 1]
            
            _logger.info("Set value of %s to %.1f", myvar, new_val2)
            await myvar2.write_value(new_val2)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(), debug=True)
