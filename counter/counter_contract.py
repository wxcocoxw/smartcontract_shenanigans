from typing import Final

from beaker.client import ApplicationClient, LogicException
from beaker import sandbox

from pyteal import *
from beaker.application import Application
from beaker.state import ApplicationStateValue
from beaker.decorators import external, create, Authorize

class Counter(Application):

    counter: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64,
        default=Int(0),
        descr="A counter using stateful Algorand Smart Contract",
    )
    
    @create
    def create(self):
        return self.initialize_application_state()

    @external
    def increment(self, *, output: abi.Uint64):
        return Seq(
            [
                self.counter.set(self.counter + Int(1)),
                output.set(self.counter),
            ]
        )

    @external
    def decrement(self, *, output: abi.Uint64):
        return Seq(
            [
                Assert(self.counter > Int(0)),
                self.counter.set(self.counter - Int(1)),
                output.set(self.counter),
            ]
        )

# counter_app = Counter(version=8)
# counter_app.dump()

def demo():
    client = sandbox.get_algod_client()

    accts = sandbox.get_accounts()
    acct = accts.pop()

    app_client = ApplicationClient(client, Counter(), signer=acct.signer)

    app_id, app_addr, txid = app_client.create()
    print(f"Created app with id {app_id} and address {app_addr}")

    app_client.call(Counter.increment)
    app_client.call(Counter.increment)
    app_client.call(Counter.increment)
    result = app_client.call(Counter.increment)
    print(f"Counter value is {result.return_value}")

    result = app_client.call(Counter.decrement)
    print(f"Counter value is {result.return_value}")


demo()