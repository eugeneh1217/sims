# HURDLES

## SUMMARY
This is a short project to explore genetic algorithms: more specifically, genetic programming.

## ENVIRONMENT
The Agent will attempt to clear procedurally generated "hurdles" (similar to google's offline dinasaur game).
The map will be moving at a pre-set speed.
Agents will be able to:
* See the next hurdle's:
    * Height
    * Distance
* Jump:
    * Initial velocity
    <!-- * Initial Angle -->

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
        * Flip: Random nodes flip to another viable node
        * Truncation: random node is removed from tree (not entire branch)
        * Swap: Random compatible nodes are swapped
        * Gaussian: Random gaussian noise is added to existing numerical node
        * Grow: Introduce a random function node (and required children value nodes)

## TODO:
### Major
* Create grammar structure
* Implement evolution operations
* Implement Environment
* Implement Agents

### Minor
* Implement binary representations (probably starting from node class)

