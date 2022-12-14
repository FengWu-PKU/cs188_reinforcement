# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from typing import Counter
import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        states=self.mdp.getStates()
        # V0=0
        for i in range(self.iterations):
            tmp=util.Counter()
            for state in states:
                tmp[state]=self.calcValue(state)
            self.values=tmp
                
                
    def calcValue(self, state):
        if self.mdp.isTerminal(state):
            return 0
        v=float('-inf')
        actions=self.mdp.getPossibleActions(state)
        for action in actions:
            tp=self.mdp.getTransitionStatesAndProbs(state, action)
            sum=0
            for i in tp:
                sum+=i[1]*(self.mdp.getReward(state,action,i[0])+self.discount*self.getValue(i[0]))
            v=max(v,sum)
        return v




    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        tps=self.mdp.getTransitionStatesAndProbs(state,action)
        q=0
        for tp in tps:
            q+=tp[1]*(self.mdp.getReward(state,action,tp[0])+self.discount*self.getValue(tp[0]))
        return q

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(state):
            return None
        qvalues=util.Counter()
        actions=self.mdp.getPossibleActions(state)
        for action in actions:
            qvalues[action]=self.computeQValueFromValues(state,action)
        return qvalues.argMax()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        states=self.mdp.getStates()
        size=len(states)
        for i in range(self.iterations):
            index=i%size
            if self.mdp.isTerminal(states[index]):
                continue
            self.values[states[index]]=self.calcValue(states[index])

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        predecessors=self.getPredecessors()
        pq=util.PriorityQueue()
        states=self.mdp.getStates()
        for state in states:
            if self.mdp.isTerminal(state):
                continue
            diff=abs(self.getValue(state)-max(self.getQValue(state,action) for action in self.mdp.getPossibleActions(state)))
            pq.push(state,-diff)
        for i in range(self.iterations):
            if pq.isEmpty():
                return
            curState=pq.pop()
            if not self.mdp.isTerminal(curState):
                self.values[curState]=self.calcValue(curState)
            for (p,prob) in predecessors[curState]:
                if self.mdp.isTerminal(p):
                    continue
                diff=abs(self.getValue(p)-max(self.getQValue(p,action) for action in self.mdp.getPossibleActions(p)))
                if diff>self.theta:
                    pq.update(p,-diff)
        


    def getPredecessors(self):
        predecessors=util.Counter()
        states=self.mdp.getStates()
        for state in states:
            predecessors[state]=set()
        for state in states:
            actions=self.mdp.getPossibleActions(state)
            for action in actions:
                tps=self.mdp.getTransitionStatesAndProbs(state,action)
                for tp in tps:
                    predecessors[tp[0]].add((state,tp[1]))
        return predecessors




