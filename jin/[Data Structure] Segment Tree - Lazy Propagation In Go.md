# Segment Tree - Lazy Propagation In Go 
미완. 코드는 다 짰고, 백준 예제도 맞았는데 너무 졸려서 일단 자보려 한다. <br>
update에서 범위를 아예 벗어날 때의 return값을 잘못 줘서 계속 틀렸었다. <br> <br>

아래 코드는  Child 배열의 1 ~ N까지 인덱스에 트리의 노드들을 저장한 형태 <br>
사이즈가 4 * N인 이유는 완전 이진 트리 형태를 만들어 주기 위해서이다.

```go
type SegmentTree struct {
	children []*SegmentTreeNode
}

func (tree *SegmentTree) GetSize() int {
	return len(tree.children) - 1
}

func (tree *SegmentTree) IsNotLeaf(nodeNumber int) bool {
	end := tree.GetSize()
	start := (end + 1) / 2
	return !(start <= nodeNumber && nodeNumber <= end)
}

type SegmentTreeNode struct {
	start, end int
	sum, lazy  int64
}

func InitSegmentTree(N int, values []int64) (tree *SegmentTree) {
	size := 2 * N
	tree = &SegmentTree{children: make([]*SegmentTreeNode, size+1)}
	for i := 0; i <= size; i++ {
		tree.children[i] = &SegmentTreeNode{}
	}
	tree.initSegmentTree(1, 1, N, values)
	return tree
}

func (tree *SegmentTree) initSegmentTree(nodeNumber, start, end int, values []int64) int64 {
	if start == end {
		node := tree.children[nodeNumber]
		node.setValues(values[start], start, end)
		return node.sum
	}

	mid := (start + end) / 2
	leftSum := tree.initSegmentTree(nodeNumber*2, start, mid, values)    // left child
	rightSum := tree.initSegmentTree(nodeNumber*2+1, mid+1, end, values) // right child

	node := tree.children[nodeNumber]
	node.setValues(leftSum+rightSum, start, end)
	return node.sum
}

func (tree *SegmentTree) Query(start, end int) int64 {
	return tree.query(1, start, end)
}

func (tree *SegmentTree) query(nodeNumber, start, end int) int64 {
	node := tree.children[nodeNumber]
	tree.pushLazy(nodeNumber)

	if start > node.end || node.start > end {
		return 0
	}

	if start <= node.start && node.end <= end {
		return node.sum
	}

	leftSum := tree.query(nodeNumber*2, start, end)
	rightSum := tree.query(nodeNumber*2+1, start, end)
	return leftSum + rightSum
}

func (tree *SegmentTree) Update(targetStart, targetEnd int, newValue int64) {
	tree.update(1, targetStart, targetEnd, newValue)
}

func (tree *SegmentTree) update(nodeNumber, targetStart, targetEnd int, newValue int64) int64 {
	node := tree.children[nodeNumber]
	tree.pushLazy(nodeNumber)

	if node.start > targetEnd || targetStart > node.end {
		return node.sum
	}

	if targetStart <= node.start && node.end <= targetEnd {
		node.sum += newValue * int64(node.end-node.start+1)
		if tree.IsNotLeaf(nodeNumber) {
			tree.children[nodeNumber*2].lazy += newValue
			tree.children[nodeNumber*2+1].lazy += newValue
		}
		return node.sum
	}

	leftSum := tree.update(nodeNumber*2, targetStart, targetEnd, newValue)
	rightSum := tree.update(nodeNumber*2+1, targetStart, targetEnd, newValue)
	node.sum = leftSum + rightSum
	return node.sum
}

func (tree *SegmentTree) pushLazy(nodeNumber int) {
	node := tree.children[nodeNumber]
	if node.lazy == 0 {
		return
	}

	node.sum += node.lazy * int64(node.end-node.start+1)
	if tree.IsNotLeaf(nodeNumber) {
		tree.children[nodeNumber*2].lazy += node.lazy
		tree.children[nodeNumber*2+1].lazy += node.lazy
	}
	node.lazy = 0
}

func (node *SegmentTreeNode) setValues(value int64, start, end int) {
	node.sum = value
	node.start = start
	node.end = end
}
```
