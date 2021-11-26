# Copyright [2020] [KTH Royal Institute of Technology] Licensed under the
# Educational Community License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may
# obtain a copy of the License at http://www.osedu.org/licenses/ECL-2.0
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing
# permissions and limitations under the License.
#
# Course: EL2805 - Reinforcement Learning - Lab 1 Problem 4
# Code author: [Alessio Russo - alessior@kth.se]
# Last update: 6th October 2020, by alessior@kth.se
#

# Load packages
import numpy as np
import gym
import torch
import matplotlib.pyplot as plt
import pickle

# Import and initialize Mountain Car Environment
env = gym.make('MountainCar-v0')
state =env.reset()
k = env.action_space.n      # tells you the number of actions
low, high = env.observation_space.low, env.observation_space.high


#Vectors Definition
p = 2
ETA = np.array([[i,j] for i in range(p+1) for j in range(p+1)])
#ETA = ETA[1:,:] #LET'S SEE WHAT HAPPENS IF WE ELIMINATE THE [0,0]
W = np.zeros((k,np.shape(ETA)[0]))

# Scaling the fourier basis


# Parameters
N_episodes = 600        # Number of episodes to run for training
momentum = 0.2          # SGD with momentum, set to 0 for normal SGD
reduce_alpha = True
reduce_counter = 0
scaling_basis = True
epsilon = 0

#Equations
discount_factor = 1.    # Value of gamma
eligibility_trace = 0.1#np.round(np.linspace(0,1,5),3) #Value of lambda
alpha_set = 0.2 #np.round(np.linspace(0,1,40),3)

# Reward
episode_reward_list = []  # Used to save episodes reward
mean_reward_episode_list = []
std_plus_reward_episode_list = []
std_less_reward_episode_list = []



# Functions used during training
def running_average(x, N):
    ''' Function used to compute the running mean
        of the last N elements of a vector x
    '''
    if len(x) >= N:
        y = np.copy(x)
        y[N-1:] = np.convolve(x, np.ones((N, )) / N, mode='valid')
    else:
        y = np.zeros_like(x)
    return y

def scale_state_variables(s, low=env.observation_space.low, high=env.observation_space.high):
    ''' Rescaling of s to the box [0,1]^2 '''
    x = (s - low) / (high - low)
    return x

def basis_function(eta, state):
    bases = np.cos(np.pi*np.matmul(eta,state))
    #this is the same as doing a bucle for and doing the dot product and appending the vlaues into a list
    return bases

def choose_action(epsilon, Q):
    """Function to choose action"""
    if np.random.uniform(0, 1) < epsilon:
        action = np.random.choice(np.arange(k))
    else:
        action = np.argmax(Q)
    return action

# Training process

    # Scaling the fourier basis
if scaling_basis:
    norm_eta = np.linalg.norm(ETA, 2, 1)
    norm_eta[norm_eta == 0] = 1  # if ||eta_i||=0 then alpha_i=alpha
    alpha = np.divide(alpha_set, norm_eta)
else:
    alpha = alpha_set


for i in range(N_episodes):
    # Reset enviroment data
    done = False
    state = scale_state_variables(env.reset(), low, high)
    total_episode_reward = 0.

    z = np.zeros((k,np.shape(ETA)[0]))
    velocity = np.zeros((k,np.shape(ETA)[0]))

    while not done:
        # Take a random action
        # env.action_space.n tells you the number of actions
        # available

        basis = basis_function(ETA, state)
        Q = np.dot(W,basis) #This vector results on [Q(action1,n bases),Q(action2,n bases),Q(action3,bases)]
        action_random = np.random.randint(0, k)
        action_maximum_Q = np.argmax(Q)

        action = choose_action(epsilon, Q)


        # Get next state and reward.  The done variable
        # will be True if you reached the goal position,
        # False otherwise
        next_state, reward, done, _ = env.step(action)
        next_state = scale_state_variables(next_state)

        # Update episode reward
        total_episode_reward += reward

        # Update state for next iteration
        state = next_state
        next_basis = basis_function(ETA, next_state)
        Q_next = np.dot(W,next_basis)
        action_next = np.argmax(Q_next)


        #Update eligibility trace
        z = discount_factor*eligibility_trace* z #discount_factor*element* z#discount_factor*eligibility_trace* z
        z[action,:] += basis
        z = np.clip(z, -5, 5)

        #Update W
        delta_t = reward + discount_factor * Q_next[action_next] - Q[action]
        if scaling_basis:
            velocity = momentum * velocity + delta_t * np.matmul(z, np.diag(alpha))
        else:
            velocity = momentum * velocity + delta_t * alpha * z
        W += velocity

    if reduce_alpha and total_episode_reward > -200:
        #ALPHA REDUCTION WORKS EXTREMELLY WELL!!!
        # If win, scale alpha by .8 or .6 if the agent wins
        reduce_counter += 1
        alpha *= 0.9 - 0.2 * (total_episode_reward > -130)

    # Append episode reward
    episode_reward_list.append(total_episode_reward)


    # Close environment
    env.close()

data = {'W':W, 'N': ETA}
with open('weights.pkl', 'wb') as f:
    pickle.dump(data,f)

"""
# Calculate mean and std for reward
mean_reward_episode_list.append(np.mean(episode_reward_list))
std_plus_reward_episode_list.append(np.mean(episode_reward_list)+np.std(episode_reward_list))
std_less_reward_episode_list.append(np.mean(episode_reward_list)-np.std(episode_reward_list))


# Plot Rewards
plt.plot([i for i in range(1, N_episodes+1)], episode_reward_list, label='Episode reward')
plt.plot([i for i in range(1, N_episodes+1)], running_average(episode_reward_list, 10), label='Average episode reward')
plt.xlabel('Episodes')
plt.ylabel('Total reward')
plt.title('Total Reward vs Episodes'+str(ind))
plt.legend()
plt.grid(alpha=0.3)
plt.show()

# Plot optimal val func
s0 = np.linspace(0,1,100)
s1 = np.linspace(0,1,100)
X, Y = np.meshgrid(s0, s1)
Z = np.array([[max(np.dot(W, basis_function(ETA, np.array([p,v])))) for p in s0] for v in s1])
fig, ax = plt.subplots()
surf = ax.pcolormesh(X, Y, Z,shading='auto')
plt.xlabel('Position')
plt.ylabel('Velocity')
plt.title('V*(pos,vel)')
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()

# Plot optimal policy
s0 = np.linspace(0,1,100)
s1 = np.linspace(0,1,100)
X, Y = np.meshgrid(s0, s1)
Z = np.array([[np.argmax(np.dot(W, basis_function(ETA, np.array([p,v])))) for p in s0] for v in s1])
fig, ax = plt.subplots()
surf = ax.pcolormesh(X, Y, Z,shading='auto')
plt.xlabel('Position')
plt.ylabel('Velocity')
plt.title('Policy (pos,vel)')
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()


fig, ax = plt.subplots(1)
default_x_ticks = range(len(eligibility_trace))
ax.plot(default_x_ticks,mean_reward_episode_list, color = 'blue')
ax.fill_between(default_x_ticks,std_less_reward_episode_list,std_plus_reward_episode_list, alpha = 0.3)

#ax.fill_between(default_x_ticks, std_plus_reward_episode_list, mu1-sigma1, facecolor='blue', alpha=0.5)

#plt.plot(default_x_ticks,std_less_reward_episode_list, std_plus_reward_episode_list, linestyle = 'dotted', color = 'blue')
ax.set_xticklabels(alpha_set, rotation=45, rotation_mode="anchor")
#plt.tight_layout()
ax.set_xlabel('Eligibility Trace value')
ax.set_ylabel('Reward')
ax.set_title('Mean reward due to eligibility trace parameter')
fig.show()
"""