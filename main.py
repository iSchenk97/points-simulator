# This is a sample Python script.
import csv
import random
from decimal import *

RUNS = 5_000_000
CUTOFF = 4
PRECISION = 8


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def parse(filename):
    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        l = []
        for row in spamreader:
            entry = (row[0], int(row[1]))
            l.append(entry)
        return l


# assigns a random placement out of the array parsed from the points csv.
def randomPlacements(teams, points):
    r = []
    results = random.sample(points, k=24)

    for team in teams:
        if team[0] == 'Acend':
            r.append([team[0], 17, team[1]])
            continue
        placement = results.pop()
        entry = [0, 0, 0]
        entry[0] = team[0]
        entry[1] = int(placement[0])
        entry[2] = (team[1] + placement[1])
        r.append(entry)
    return r


# sorts the arrays by placement in the recent event
def sortPlacements(placements):
    def takeSecond(elem):
        return elem[2]

    for team in placements:
        sortedTeams = sorted(placements, key=takeSecond, reverse=True)
        return sortedTeams


# goes through one team, and filters out where they finished in the last tournament,
# and what that meant on the overall scoreboard
def checkTeam(arrays, team):
    teamName = team[0]
    resultList = [teamName]
    for array in arrays:
        for index, team, in enumerate(array):
            if team[0] == teamName:
                entry = (team[1], team[2], index + 1)
                resultList.append(entry)
                break
    return resultList


## further data processing, forgot what this does
def getData(tuple):
    newTuple = tuple[1:]
    myList = [tuple[0]]
    for i in range(1, 25):
        if not list(filter(lambda element: element[0] == i, newTuple)):
            continue
        else:
            myList.append(list(filter(lambda element: element[0] == i, newTuple)))
    return myList


## gets a summary of the results of this team
def summarizeResults(data):
    newData = data[1:]
    summary = []
    for i in range(len(newData)):
        summary.append([newData[i][0][0]])
        for outcome in newData[i]:
            summary[i].append(outcome[2])
    return summary


## format data to make it ready for statistic analysis
def formatResults(summary):
    results = []
    for i in range(len(summary)):
        result = summary[i][0]
        temp = []
        for outcome in summary[i][1:]:
            if not temp:
                temp.append([result, [outcome, 1]])
            else:
                found = False
                for recentOutcome in temp[0][1:]:
                    if recentOutcome[0] == outcome:
                        recentOutcome[1] += 1
                        found = True
                        break
                if not found:
                    temp[0].append([outcome, 1])
        results.extend(temp)
    return results


# calculates the odds a team will finish in x place on the leaderboard, based on y placement in the last tournament
def calculateOdds(results):
    for i in range(len(results)):
        temp = []
        outcomes = results[i][1:]
        sum = Decimal(0)
        counts = []
        for outcome in outcomes:
            freq = Decimal(outcome[1])
            sum += freq
            counts.append(freq)
        temp.extend(list(map(lambda count: Decimal(count) / sum, counts)))
        for j in range(len(temp)):
            entry = Decimal(temp[j])
            results[i][1:][j].append(entry)
    return results


# formats the odds in a better way
def oddsPlacement(results):
    odds = []
    for result in results:
        outcome = (result[1][0])
        odd = result[1][2]
        odds.append(result[0])
        entry = []
        if odd == 1:
            entry.append([outcome, Decimal(odd)])
            odds.append(entry)
            continue
        for oneOutcome in result[1:]:
            addition = [oneOutcome[0], Decimal(oneOutcome[2])]
            entry.append(addition)
        odds.append(entry)
    return odds


# calculates the odds to qualify based on where the cutoff on the total leaderboard is
def oddsQual(data):
    chances = []
    for i in range(len(data)):
        if i % 2 == 1:
            continue
        current = data[i]
        qualChance = Decimal(0)
        for outcome in data[i + 1]:
            if outcome[0] <= CUTOFF:
                qualChance += outcome[1]
        if abs(qualChance - round(qualChance)) < 0.00001:
            qualChance = round(qualChance)
        chances.append((current, qualChance))
    return chances


def pgc(teams, points):
    array = []
    for i in range(10):
        placements = randomPlacements(teams, points)
        sortedTeams = sortPlacements(placements)
        array.append(sortedTeams)
    teamResults = checkTeam(array, teams)
    data = getData(teamResults)
    calculateOdds(data)


def export(data):
    teams = []
    for i in range(len(data)):
        entry = [data[i][0]]
        for percent in data[i][1]:
            entry.append(percent[1])
        teams.append(entry)
    with open('results.csv', 'w', newline='', ) as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for team in teams:
            spamwriter.writerow(team)
    print(teams)


def pgs(teams, points):
    array = []
    for i in range(RUNS):
        #print("Simulations run: ", i)
        placements = randomPlacements(teams, points)
        sortedTeams = sortPlacements(placements)
        array.append(sortedTeams)
    allOdds = []
    for team in teams:
        teamResults = checkTeam(array, team)
        data = getData(teamResults)
        summary = summarizeResults(data)
        formatted = formatResults(summary)
        odds = calculateOdds(formatted)
        placeOdds = oddsPlacement(odds)
        final = oddsQual(placeOdds)
        allOdds.append([team[0], final])
    export(allOdds)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # pgs.csv is the list of teams and their current pgs points
    teams = parse('pgs.csv')
    # pgs2 is the list of placements and what amount of pgs points each team gets
    points = parse('pgs2.csv')
    pgs(teams, points)
    # teams = parse('pgc.csv')
    # points = parse('fall.csv')
    # pgc(teams, points) 