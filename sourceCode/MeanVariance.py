from scipy import linalg
class MeanVariance:
    def __init__(self, returns):
        self.returns = returns
    
    #定义最小化方差的函数，求解二次规划
    def minVar(self, goalRet):
        covs = np.array(self.returns.cov())
        means = np.array(self.returns.mean())
        L1 = np.append(np.append(covs.swapaxes(0,1),[means],0),
                      [np.ones(len(means))],0).swapaxes(0,1)
        L2 = list(np.ones(len(means)))
        L2.extend([0,0])
        L3 = list(means)
        L3.extend([0,0])
        L4 = np.array([L2,L3])
        L = np.append(L1,L4,0)
        results = linalg.solve(L,np.append(np.zeros(len(means)),[1,goalRet],0))
        return (np.array([list(self.returns.columns), results[:-2]]))
    
    # 定义绘制最小方差曲线函数
    def frontierCurve(self):
        goals = [x/500000 for x in range(-100, 4000)]
        variances = list(map(lambda x: self.calVar(self.minVar(x)[1,:].astype(np.float)),goals))
        plt.plot(variances, goals)
        
    #给定个资产的比例，计算收益率均值
    def meanRet(self, fracs):
        meanRisky = ffn.to_returns(self.returns).mean()
        assert len(meanRisky) == len(fracs), 'Length of fractions must be equal to nuber of assets'
        return(np.sum(np.multiply(meanRisky, np.array(fracs))))
    
    #给定各资产的比例，计算收益率方差
    def calVar(self, fracs):
        return (np.dot(np.dot(fracs, self.returns.cov()), fracs))
