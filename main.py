from pyryanair import PyRyanAir


def main():
    agent = PyRyanAir()
    agent.userInputs()
    print(agent.export_flights)
    # agent.getRoutes('RBA')


if __name__ == '__main__':
    main()
