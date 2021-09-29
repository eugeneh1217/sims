# HURDLES

## SUMMARY
This is a short project to explore genetic algorithms: more specifically, genetic programming.

## ENVIRONMENT
The AI will attempt to clear procedurally generated "hurdles" (similar to google's offline dinasaur game).
It will be able to:
* See the next hurdle's:
    * Hheight
    * Distance
* Jump with an initial velocity within a restricted domain
The map will be moving at a pre-set speed.

## GENETIC PROGRAMMING
* From a domain of vocabulary and grammar, generate a decision tree.
    * These decision trees will determine the behavior of the instance
* Fitness function: used to evaulate the performance of instances.
    * Will probably be total distance covered for this problem
* Operations to progress evolution
    * Crossover
        * Select a random "break points" within each parent
        * Exchange the branches below the break point
        * This operation results in the *permuation problem*.
    * Mutation Operators
        * Random nodes flip to another viable node
        * Truncation: random node is removed from tree (not entire branch)
        * Random terminal nodes are swapped
        * Add random gaussian noise to existing values
        * Grow by introducing a random function node (and required children value nodes)

