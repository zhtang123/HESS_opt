#include <bits/stdc++.h>
#include <chrono>
#include <fstream>

using namespace std;

namespace Tzh {

    const int maxn = 10000, maxm = 1000000;
    int n, capacity = 50000, max_demand, max_price, min_price, max_transmission_cost, save_cost = 0;

    long long demand[maxn][24], price[maxn][24], transmission_cost[maxn][maxn];
    long long delta_price[maxn], rank[maxn];
    long long dp[25][50010];

    ofstream logFile;
    ofstream resultFile;

    // Function to read data from a file
    void readdata(const string &filename) {
        ifstream dataFile(filename);

        if (!dataFile) {
            cerr << "Failed to open data file." << endl;
            exit(1);
        }

        // Read constants
        string label;
        dataFile >> label >> n;
        dataFile >> label >> max_demand;
        dataFile >> label >> max_price;
        dataFile >> label >> min_price;
        dataFile >> label >> max_transmission_cost;

        // Read demand
        dataFile >> label;
        for (int i = 1; i <= n; i++)
            for (int j = 0; j < 24; j++)
                dataFile >> demand[i][j];

        // Read price
        dataFile >> label;
        for (int i = 1; i <= n; i++)
            for (int j = 0; j < 24; j++)
                dataFile >> price[i][j];

        // Read transmission cost
        dataFile >> label;
        for (int i = 1; i <= n; i++)
            for (int j = 1; j <= n; j++)
                dataFile >> transmission_cost[i][j];

        dataFile.close();
    }

    // Function to calculate the cost for a specific hour
    int cal_hour_cost(int hour) {
        int sum = 0;
        for (int i = 1; i <= n; i++)
            sum += demand[i][hour] * price[i][hour];
        return sum;
    }

    // Function to calculate the basic cost for all cities and hours
    int cal_basic_cost() {
        int sum = 0;
        for (int i = 1; i <= n; i++)
            for (int j = 0; j < 24; j++)
                sum += demand[i][j] * price[i][j];
        return sum;
    }

    // Function to get the unique ID for a city-hour pair
    int get_id(int city, int hour) {
        return (city) * 24 + hour;
    }

    struct ed {
        int next, to, w, c;
    } e[maxm];

    int cnt = 1, head[maxn];
    int inf = 0x3f3f3f3f;
    int mid_node[maxn][25];

    // Function to add edges to the graph
    void add(int u, int v, int w, int c) {
        e[++cnt] = (ed) { head[u], v, w, c }; head[u] = cnt;
        e[++cnt] = (ed) { head[v], u, 0, -c }; head[v] = cnt;
    }

    const int S = 1, T = 2;
    int dis[maxn], nxt[maxn], ter[maxn], cap[maxn], cost[maxn], vis[maxn], cur[maxn], ret;

    // Function to initialize the graph and reset variables
    void init() {
        memset(head, 0, sizeof(head));
        cnt = 1; ret = 0;
    }

    // SPFA algorithm to find the shortest path in the residual graph
    bool spfa(int s, int t) {
        memset(dis, 0x3f, sizeof(dis));
        memcpy(cur, head, sizeof(head));
        queue<int> q;
        q.push(s); dis[s] = 0; vis[s] = 1;
        while (!q.empty()) {
            int u = q.front();
            q.pop(); vis[u] = 0;
            for (int i = head[u]; i; i = e[i].next) {
                int v = e[i].to;
                if (e[i].w && dis[v] > dis[u] + e[i].c) {
                    dis[v] = dis[u] + e[i].c;
                    if (!vis[v]) q.push(v), vis[v] = 1;
                }
            }
        }
        return dis[t] != inf;
    }

    // DFS to find the augmenting path and update the flow
    int dfs(int u, int t, int flow) {
        if (u == t) return flow;
        vis[u] = 1;
        int ans = 0;
        for (int &i = cur[u]; i; i = e[i].next) {
            int v = e[i].to;
            if (e[i].w && dis[v] == dis[u] + e[i].c && !vis[v]) {
                int x = dfs(v, t, min(e[i].w, flow - ans));
                if (x) ret += x * e[i].c, e[i].w -= x, e[i ^ 1].w += x, ans += x;
            }
        }
        vis[u] = 0;
        return ans;
    }

    // Min-Cost Max-Flow algorithm
    int mcmf(int s, int t) {
        int ans = 0;
        while (spfa(s, t)) {
            int x;
            while ((x = dfs(s, t, inf))) ans += x;
        }
        return ans;
    }

    // Function to construct the graph for the problem
    void make_graph(int *city) {
        int cur = get_id(n, 24);

        for (int i = 1; i <= n; i++)
            if (city[i])
                for (int j = 0; j < 24; j++)
                    mid_node[i][j] = ++cur;

        for (int i = 1; i <= n; i++)
            for (int j = 0; j < 24; j++) {
                add(S, get_id(i, j), inf, price[i][j]);
                add(get_id(i, j), T, demand[i][j], 0);
            }

        for (int k = 1; k <= n; k++)
            if (city[k])
                for (int j = 0; j < 24; j++)
                    for (int i = 1; i <= n; i++)
                        add(mid_node[k][j], get_id(i, j), inf, transmission_cost[k][i]);

        for (int k = 1; k <= n; k++)
            if (city[k])
                for (int j = 0; j < 24; j++) {
                    add(get_id(k, j), mid_node[k][j + 1], capacity, save_cost);
                    add(mid_node[k][j], mid_node[k][j + 1], capacity, save_cost);
                }
    }

    int placed_cities[maxn];

    // Function to generate a random number between 0 and 1
    double Rand() { return (double)rand() / RAND_MAX; }

    // Simulated Annealing algorithm to find the optimal placement of cities
    int simulateAnneal(int cost) {
        double t = 1000000;
        int ans = 0x3f3f3f3f;
        int last = 0x3f3f3f3f;

        auto start = chrono::high_resolution_clock::now();
        auto ct = chrono::high_resolution_clock::now();

        while (t > 0.01) {
            auto nt = chrono::high_resolution_clock::now();
            chrono::duration<double> duration = nt - start;
            auto current_time = chrono::system_clock::to_time_t(chrono::system_clock::now());

            int id = rand() % n + 1;
            placed_cities[id] ^= 1;
            int num = 0;
            for (int i = 1; i <= n; i++) num += placed_cities[i];
            init();
            make_graph(placed_cities);
            int flow_cost = mcmf(S, T);
            int cur = ret + cost * num;
            ans = min(ans, cur);
            double delta = cur - last;

            string log_entry = "Time: " + string(ctime(&current_time)) + " Flow Cost: " + to_string(flow_cost) +
                            ", Total Cost: " + to_string(cur) + ", Cities: ";
            for (int i = 1; i <= n; i++) log_entry += to_string(placed_cities[i]) + " ";
            log_entry += "\n";

            logFile << log_entry;
            cout << log_entry;

            if (exp(-delta / t) > Rand()) {
                last = cur;
            } else {
                placed_cities[id] ^= 1;
            }

            string result_entry = "Temperature: " + to_string(t) + ", Total Cost: " + to_string(cur) +
                                ", Elapsed Time: " + to_string(duration.count()) + " seconds\n";
            resultFile << result_entry;

            t *= 0.98;
        }

        auto end = chrono::high_resolution_clock::now();
        chrono::duration<double> elapsed = end - start;

        string final_log = "Total time elapsed: " + to_string(elapsed.count()) + " seconds\n";
        final_log += "Final cost: " + to_string(ans) + "\n";

        logFile << final_log;
        cout << final_log;

        return ans;
    }


    // Main function to run the model
    void work() {
        srand(233);

        readdata("generated_data.txt");

        string basic_cost_log = "Basic cost: " + to_string(cal_basic_cost()) + "\n";
        logFile << basic_cost_log;
        cout << basic_cost_log;

        int dem_total = 0;
        for (int i = 1; i <= n; i++)
            for (int j = 0; j < 24; j++)
                dem_total += demand[i][j];

        make_graph(placed_cities);

        int ans = simulateAnneal(5000000);

        string final_result_log = "Final cost: " + to_string(ans) + "\nTotal flow cost: " + to_string(ret) + "\nTotal demand: " + to_string(dem_total) + "\n";

        logFile << final_result_log;
        cout << final_result_log;

        logFile.close();
        resultFile.close();
    }
}

int main() {
    Tzh::logFile.open("log.txt");
    Tzh::resultFile.open("result.txt");
    Tzh::work();
    return 0;
}
