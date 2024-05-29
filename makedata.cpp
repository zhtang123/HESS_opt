#include <bits/stdc++.h>
#include <fstream>
#include <cstdlib>

using namespace std;

const int n = 100;
const int max_demand = 1000;
const int max_price = 200;
const int min_price = 50;
const int max_transmission_cost = 1;

void makedata(long long demand[n + 1][24], long long price[n + 1][24], long long transmission_cost[n + 1][n + 1]) {
    for (int i = 1; i <= n; i++)
        for (int j = 0; j < 24; j++)
            demand[i][j] = rand() % max_demand;

    for (int i = 1; i <= n; i++)
        for (int j = 0; j < 24; j++)
            price[i][j] = rand() % (max_price - min_price) + min_price;

    for (int i = 1; i <= n; i++)
        for (int j = i + 1; j <= n; j++)
            transmission_cost[i][j] = transmission_cost[j][i] = rand() % max_transmission_cost;
}

int main() {
    srand(time(0)); // Seed the random number generator with the current time

    long long demand[n + 1][24], price[n + 1][24], transmission_cost[n + 1][n + 1];
    makedata(demand, price, transmission_cost);

    ofstream dataFile("generated_data.txt");

    if (!dataFile) {
        cerr << "Failed to open file for writing." << endl;
        return 1;
    }

    // Output constants
    dataFile << "n " << n << endl;
    dataFile << "max_demand " << max_demand << endl;
    dataFile << "max_price " << max_price << endl;
    dataFile << "min_price " << min_price << endl;
    dataFile << "max_transmission_cost " << max_transmission_cost << endl;

    // Output demand
    dataFile << "demand" << endl;
    for (int i = 1; i <= n; i++) {
        for (int j = 0; j < 24; j++) {
            dataFile << demand[i][j] << " ";
        }
        dataFile << endl;
    }

    // Output price
    dataFile << "price" << endl;
    for (int i = 1; i <= n; i++) {
        for (int j = 0; j < 24; j++) {
            dataFile << price[i][j] << " ";
        }
        dataFile << endl;
    }

    // Output transmission cost
    dataFile << "transmission_cost" << endl;
    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= n; j++) {
            dataFile << transmission_cost[i][j] << " ";
        }
        dataFile << endl;
    }

    dataFile.close();
    cout << "Data generated and written to generated_data.txt" << endl;

    return 0;
}
