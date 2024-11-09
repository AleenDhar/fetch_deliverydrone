# Import Required libraries
import requests
import os
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from pymavlink import mavutil

# Define Request and Response Models
class DeliveryReq(Model):
    gps_loc: list

class DroneResponse(Model):
    drone_res : list


class ErrorResponse(Model):
    error : str

 

def wait_conn():
    """
    Sends a ping to stabilish the UDP communication and awaits for a response
    """
    msg = None
    while not msg:
        master.mav.ping_send(
            int(time.time() * 1e6), # Unix time in microseconds
            0, # Ping number
            0, # Request ping of all systems
            0 # Request ping of all components
        )
        msg = master.recv_match()
        time.sleep(0.5)



# Define News Agent
DroneAgent = Agent(
    name="DroneAgent",
    port=8000,
    seed="Fly the drone high",
    endpoint=["http://127.0.0.1:8000/submit"],
)

master = mavutil.mavlink_connection("/dev/ttyACM0", baud=115200)
# Registering agent on Almanac and funding it.
fund_agent_if_low(DroneAgent.wallet.address())
 
# On agent startup 
@DroneAgent.on_event('startup')
async def agent_details(ctx: Context):
    #  Sends a ping to estabilish the UDP communication and awaits for a response
    wait_conn()
    ctx.logger.info(f'Search Agent Address is {DroneAgent.address}')
 
# On_query handler 
@DroneAgent.on_query(model=DeliveryReq, replies={DroneResponse})
async def query_handler(ctx: Context, sender: str, msg: DeliveryReq):
    try:
        ctx.logger.info(f'Preparing the drone to move to coordinates gps_loc: {msg.gps_loc}')

        # Arm
        master.arducopter_arm()
        print("Waiting for the vehicle to arm")
        master.motors_armed_wait()
        print('Armed!')

        # Change the fligt mode
        # mode = 'GUIDED'
        master.mav.send(mavutil.mavlink.MAVLink_set_position_target_global_int_message(10, master.target_system,
                        master.target_component,
                        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                        int(0b110111111000),
                        int( msg.gps_loc[0]* 10 ** 7), #lat * 1e7
                        int( msg.gps_loc[1] * 10 ** 7), #long * 1e7
                        10, 
                        0, 
                        0, 
                        0, 
                        0, 
                        0, 
                        0, 
                        1.57, 
                        0.5
                        ))
        # Disarm
        master.arducopter_disarm()
        master.motors_disarmed_wait()

        await ctx.send(sender, DroneResponse(drone_res=["drone_res","drone_res"]))

    except Exception as e:
        error_message = f"Error : {str(e)}"
        ctx.logger.error(error_message)
        # Ensure the error message is sent as a string
        await ctx.send(sender, ErrorResponse(error=str(error_message)))
 

 
if __name__ == "__main__":
    DroneAgent.run()