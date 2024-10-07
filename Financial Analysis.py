# Financial Analysis Library
# These are classes and functions that can be called in other scripts.

import numpy as np

class Asset:
    """
    An asset must have an initial capital investment but all others are optional
    Not all assets will have the same properties
    Methods within the class only need "self" passed as an argument to access any of the information
    passed into the class


    When creating a new Asset: years = len(cash_flows)
    This makes life EASY and prevents errors
    """
    def __init__(self,name,initial_capital,discount,years=None,returns=None,cash_flows=None,lower_expense_weight=None,upper_expense_weight=None):
        """
        cash_flows can be dividends

        If you use cash_flows rather than returns for a real estate asset, you must remember to use the
        lower and upper expense weights
        """
        if cash_flows is not None:
            if lower_expense_weight is None or upper_expense_weight is None:
                raise ValueError("You must provide expense weights when using cash_flows")

        if discount < 0:
            raise ValueError("discount cannot be negative")

        self.name = name
        self.initial_capital = initial_capital
        self.returns = returns if returns is not None else []
        self.cash_flows = cash_flows if cash_flows is not None else []
        self.years = years if years is not None else (len(cash_flows) if cash_flows is not None else (len(self.returns) if self.returns is not None else 0))
        self.discount = discount
        self.lower_expense_weight = lower_expense_weight if lower_expense_weight is not None else 0
        self.upper_expense_weight = upper_expense_weight if upper_expense_weight is not None else 0

    def PercentReturns(self):
        """
        Converts cash flows to percent returns
            Can be year over year or day over day; it doesn't matter

        Returns:
            A list of percent returns
        """
        cash_flows = self.cash_flows
        percent_returns = [0]
        for i in range(1,len(cash_flows)):
            previous_income = cash_flows[i-1]
            next_income = cash_flows[i]
            if previous_income != 0:
                pr = (next_income - previous_income)/previous_income
                percent_returns.append(pr*100)
            else:
                percent_returns.append(None)
        return percent_returns

    def DiscountCashFlow(self):
        """
        Calculates the discounted cash flows

        Returns:
            List of discounted cash flows
        """
        cash_flows = self.cash_flows
        years = self.years
        discount = self.discount
        dcfs = []
        years = [year for year in range(1,years+1)]
        for cash,year in zip(cash_flows,years):
            dcf = cash/(1+discount)**year
            dcfs.append(dcf)
        return dcfs
    
    def NetPresentValue(self):
        """
        Calculates the net present value of cash flows.
            Discount Cash Flow - Initial Investment

        Returns:
            The net present value of cash flows
        """
        if self.cash_flows is None:
            raise ValueError("Must have cash flows for NPV analysis.")
        dcfs = self.DiscountCashFlow()
        npv = -self.initial_capital + np.sum(dcfs)
        return npv

    def AdjustForExpenses(self):
        """
        Adjusts discounted cash flows for random expenses within a given range
        """
        adjusted_cash_flows = []
        cash_flows = self.DiscountCashFlow()
        rnd_expense_weight = np.random.uniform(self.lower_expense_weight,self.upper_expense_weight)
        for cash in cash_flows:
            adj_cash = cash*(1-rnd_expense_weight)
            adjusted_cash_flows.append(adj_cash)
        return adjusted_cash_flows
    
    def SharpeRatio(self):
        """
        Calculates the Sharpe Ratio (the retun on risk)

        Returns:
            Sharpe Ratio
        """
        if self.returns:
            returns = self.returns
        else:
            adjusted_cash_flows = self.AdjustForExpenses()
            returns = self.PercentReturns(adjusted_cash_flows)[1:]
        average_return = np.mean(returns)
        volatility = np.std(returns)
        print(f"Average Return: {average_return}")
        print(f"Volatility: {volatility}")
        sharpe_ratio = average_return / volatility
        return sharpe_ratio
    
    def PayBackPeriod(self):
        """
        Calculates how many years it will take to recover the initial investment of an asset
        based on cumulative DCFs

        Returns:
            Year in which initial capital will be recovered.
        """
        cumulative_cash_flow = 0
        for year,cash_flow in enumerate(self.DiscountCashFlow(),start=1):
            cumulative_cash_flow += cash_flow
            if cumulative_cash_flow >= self.initial_capital:
                return year
        return "Inital capital not recovered within the given cash flows."

    def AnnualWorth(self):
        """
        Calculates the annual worth of an investment that will pay every year.
        The amount that is paid is usually fixed, but you can use cash flows.

        * Useful in calculating year over year returns
            * Adjusted discounted cash flow for each year divided by the annual worth = cap rate for the year
            * Do this for each year to get each cap rate
            * Use this data to calculate year over year returns on the property.

        Annual worth is before there is any income: Is it worth more each year than I am paying for it?
            * After that you start to analyze incomes.

        Returns:
            The annual worth of an asset based on it's initial capital and discount rate
        """
        if self.years == 0:
            raise ValueError("You cannot calculate annual worth with zero years. Assign a value when you create an instance of Asset()")
        initial_investment = self.initial_capital
        debt_remaining = 0
        annuity_factor = (1-(1+self.discount)**-self.years) / self.discount
        annual_worth = (initial_investment - debt_remaining) / annuity_factor
        return annual_worth
    
    def AverageReturn(self):
        """
        Calculates the mean return based on percent returns.

        Returns:
            Average return
        """
        if self.returns is None:
            raise ValueError("You must have an array of returns to calculate the average return.")
        pct_returns = self.PercentReturns()
        avg_return = np.mean(pct_returns)
        return avg_return
    
    def Summary(self):
        print("#"*80)
        print(f"Asset: {self.name}")
        print(f"Initial Capital: {self.initial_capital}")
        print(f"Average Return: {self.AverageReturn()}")
        print(f"Discount rate: {self.discount}")
        print(f"Returns: {self.returns if self.returns is not None else 'Not Provided'}")
        print(f"Cash Flows: {self.cash_flows if self.cash_flows is not None else 'Not Provided'}")
        print(f"Years Planned to Hold: {self.years if self.years is not None else 'Not Specified'}")
        print(f"Payback Period: {self.PayBackPeriod()}")
        print(f"Annual Worth: {self.AnnualWorth()}")
        print("#"*40)
        print(f"Annual Cash Flows (discounted): {self.DiscountCashFlow()}")
        print("#"*40)
        print(f"Incomes Adjusted for Expenses: {self.AdjustForExpenses()}.\nExpense Weights:\nLower: {self.lower_expense_weight} Upper: {self.upper_expense_weight}")
        print("#"*80)
    
class Portfolio:
    """
    The Portfolio class contains instances of the Asset Class.
    There can be multiple Portfolios created.

    In order to instantiate a portfolio, Assets must first be instantiated and passed as arguments.
    """
    def __init__(self):
        """
        Constructor making Portfolio() a container for assets
        """
        self.assets = []

    def GetAssetName(self,asset):
        name = asset.name
        return name

    def Add(self,asset):
        """
        Adds an asset to the Portfolio()
        """
        self.assets.append(asset)

    def TotalMoneyInvested(self):
        """
        Calculates the total amount of money invested across all assets in the Portfolio()

        Returns:
            The sum of all initial capital
        """
        return sum(asset.initial_capital for asset in self.assets)
    
    def Correlation(self,asset1,asset2):
        """
        Calculates the correlation coefficient of the returns of any pair of assets passed as arguments
        Checks if the asset has returns or cash flows; if it is a cash flow asset, the PercentReturns()
        function is called to use the appropriate data.

        Returns:
            Correlation of the given pair.
        """
        one = asset1.returns if asset1.returns else asset1.PercentReturns()
        two = asset2.returns if asset2.returns else asset2.PercentReturns()
        rho = np.corrcoef(one,two)[1,0]
        return rho
    
    def PrintAllCorrelationCoefficients(self):
        for i in range(len(self.assets)):
            for j in range(i + 1, len(self.assets)):
                asset1 = self.assets[i]
                asset2 = self.assets[j]
                cor = self.Correlation(asset1, asset2)
                print(f"Correlation between {asset1.name} and {asset2.name}: {cor}")

    def ReturnAllCorrelationCoefficients(self):
        coefficients = []
        for i in range(len(self.assets)):
            for j in range(i+1,len(self.assets)):
                asset1 = self.assets[i]
                asset2 = self.assets[j]
                cor = self.Correlation(asset1,asset2)
                coefficients.append(cor)
        return coefficients
    
    def StandardDeviation(self,asset):
        """
        Calculates the standard deviation of the returns of an asset.
        If the asset has cash flows, the function uses the PercentReturns()
        function to create returns.

        Returns:
            The standard deviation of the returns
        """
        data = asset.returns if asset.returns else asset.PercentReturns()
        std = np.std(data)
        return std

    def PrintAllStandardDeviations(self):
        """
        Prints the standard deviation of returns for every asset in the portfolio
        """
        for asset in self.assets:
            print(f"Standard deviation for {asset.name}: {self.StandardDeviation(asset)}")

    def ReturnAllStandardDeviations(self):
        """
        Returns the standard deviation for all assests in the portfolio
        in list format for calculation purposes (Portfolio Standard Deviation)

        Returns:
            A list of standard deviations
        """
        stds = []
        for asset in self.assets:
            s = self.StandardDeviation(asset)
            stds.append(s)
        return stds
    
    def ExpectedReturn(self):
        """
        Calculates the expected return of the portfolio.

        It divides the initial capital of each asset by the total
        invested in the portfolio to find the weights and stores them in a list.

        It calculates the average return of each asset and stores them in a list.

        It calculates the sumproduct of the average returns and the weights.

        Returns:
            The expected return of the portfolio
        """
        assets = self.assets
        avg_rtrns = []
        for asset in assets:
            avg_rtrn = np.mean(asset.returns if asset.returns else asset.PercentReturns())
            avg_rtrns.append(avg_rtrn)
        
        weights = []
        for asset in assets:
            initial_capital = asset.initial_capital
            weight = initial_capital / self.TotalMoneyInvested()
            weights.append(weight)
        
        for wt in weights:
            print(wt)

        expected_return = np.dot(avg_rtrns,weights)
        return expected_return
    
    def PrintExpectedReturnData(self):
        """
        Calculates and prints the data associated with the expected return of the portfolio.

        It divides the initial capital of each asset by the total
        invested in the portfolio to find the weights and stores them in a list.

        It calculates the average return of each asset and stores them in a list.

        It calculates the sumproduct of the average returns and the weights.

        It calculates the expected return of the portfolio using the np.dot() (sumproduct)

        Prints a readable summary of the average return of the portfolio,
        the average return of each assets, and the weights calculated for each asset.
        """
        assets = self.assets
        avg_rtrns = []
        for asset in assets:
            avg_rtrn = np.mean(asset.returns if asset.returns else asset.PercentReturns())
            avg_rtrns.append(avg_rtrn)
        
        weights = []
        for asset in assets:
            initial_capital = asset.initial_capital
            weight = initial_capital / self.TotalMoneyInvested()
            weights.append(weight)

        expected_return = np.dot(avg_rtrns,weights)

        print("*"*40)
        print(f"Expected Return: {expected_return*100}%")
        print(f"Sum of weights: {np.sum(weights)}")
        print("*"*40)
        for asset,rtrn,wt in zip(assets,avg_rtrns,weights):
            rtrn*=100
            print(f"{asset.name}:\nWeight: {wt}\nAverage Return: {rtrn:.4f}%\n**************************")

# Code for testing  
stock_returns = [0.09,0.07,0.11,0.13,0.10,0.06,0.05,0.14,0.19,0.20]
stock_returns2 = [0.05,0.17,0.13,-0.05,0.20,0.16,0.09,0.11,0.12,0.04]
stock = Asset("ABC",2100,returns=stock_returns,discount=0.17)
stock2 = Asset("XYZ",3600,discount=0.14,returns=stock_returns2)

portfolio1 = Portfolio()
portfolio1.Add(stock)
portfolio1.Add(stock2)

portfolio1.PrintExpectedReturnData()
#print(f"Standard deviation of {portfolio1.GetAssetName(house2)}: {portfolio1.StandardDeviation(house2)}")
#portfolio1.PrintAllStandardDeviations()
#print(f"Standard Deviations: {portfolio1.ReturnAllStandardDeviations()}")