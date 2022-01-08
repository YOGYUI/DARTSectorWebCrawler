/* 
* 필요한 함수 선언 
*/
// jsTree 노드의 부모 노드들의 id와 text 어레이로 반환
function fnGetParents(treeObj, node) {
    parents = [];
    for (i = 0; i < node.parents.length - 1; i++) {
        parent_node_id = node.parents[i];
        parent_node = treeObj.get_node(parent_node_id);
        parents.push({id: parent_node_id, text: parent_node.text});
    }
    parents.reverse();
    
    return parents;
}

// jsTree 최하위노드 재귀검색
function fnTreeGetLeafNodes(treeObj, node, arrCollector) {
    var child_id_arr = node.children;    // 노드의 자식 노드들의 id 문자열이 담긴 어레이를 가져온다
    var arrCollector = (arrCollector) ? arrCollector : [];

    for (var i = 0; i < child_id_arr.length; ++i) {
        var node_id = child_id_arr[i];
        var nodeChild = treeObj.get_node(node_id);    // 트리의 노드 객체를 가져온다
        if (tree.is_leaf(node_id)) {
            // 잎노드일 경우 (최하위 노드)
            arrCollector.push({
                node_id: node_id,
                node_text: nodeChild.text,
                parents: fnGetParents(treeObj, nodeChild),
                corp_info_arr: []
            });
        } else {
            // 최하위 노드가 아니면 재귀호출
            arrCollector = fnTreeGetLeafNodes(treeObj, nodeChild, arrCollector);
        }
    }

    return arrCollector;
}

// 비동기 delay
function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
}

// search 함수 호출 후 <table>에서 기업 정보 가져오기
async function fnGetCorpNamesFromTableSearch(index, corp_info_arr, node_id, delay_ms_table) {
    if (index > 1) {
        search(index);
        await sleep(delay_ms_table);
    }

    var corp_info_arr = (corp_info_arr) ? corp_info_arr : [];
    var table = document.getElementsByTagName("table")[0];
    var tbody = table.getElementsByTagName("tbody")[0];
    var tr_list = tbody.getElementsByTagName("tr");

    for (i = 0; i < tr_list.length; i++) {
        tr = tr_list[i];
        td = tr.getElementsByTagName("td")[0];
        span = td.getElementsByTagName("span")[0];
        a = span.getElementsByTagName("a")[0];
        // 기업 이름 (\r, \n, \t 문자 정규식 통해 치환)
        corp_name = a.text;
        corp_name = corp_name.replace(/(\r\n|\n|\r|\t)/gm,"");
        // 기업 고유 코드 (8자리)는 href 속성 문자열 파싱
        href = a.getAttribute('href');
        index1 = href.indexOf("'");
        index2 = href.slice(index1 + 1, href.length + 1).indexOf("'") + index1;
        unique_code = href.slice(index1 + 1, index2 + 1);

        info = {
            name: corp_name,
            code: unique_code,
            sector: node_id
        };
        corp_info_arr.push(info);
    }
    
    return corp_info_arr;
}

// 페이지 여러개에 대한 비동기 순차 테이블 조회
async function fnGetCorpNamesFromTableAll(corp_info_arr, node_id, delay_ms_table) {
    var pageInfo = document.getElementsByClassName("pageInfo");
    var pageSkip = document.getElementsByClassName("pageSkip")[0];
    try {
        var li_tags = pageSkip.getElementsByTagName("li");
        var arrIndex = [];
        for (i = 0; i < li_tags.length; i++) {
            arrIndex.push(i + 1);
        }
    
        await arrIndex.reduce((prevTask, currTask) => {
            return prevTask.then(() => fnGetCorpNamesFromTableSearch(
                currTask, corp_info_arr, node_id, delay_ms_table));
        }, Promise.resolve());
    } catch (error) {
        // 해당 종목에 회사가 아예 없으면 pageSkip 태그가 없다! (TypeError 발생)
        ;
    }
}

// 트리 노드 선택 후 테이블에서 기업 정보 가져오기
async function fnSelectNodeAndGetCorpNamesFromTableAll(leaf_node_dict, treeObj, delay_ms_node, delay_ms_table) {
    // 트리 노드 선택 - 딜레이
    var node_id = leaf_node_dict.node_id;
    treeObj.select_node(node_id);
    
    await sleep(delay_ms_node);

    // 테이블에서 모든 기업 정보 가져오기
    var corp_info_arr = []
    await fnGetCorpNamesFromTableAll(corp_info_arr, node_id, delay_ms_table);
    // 기업 정보를 가져온 뒤 결과를 딕셔너리 내의 어레이에 concat
    if (corp_info_arr.length > 0) {
        leaf_node_dict.corp_info_arr = leaf_node_dict.corp_info_arr.concat(corp_info_arr);
        console.log(leaf_node_dict.node_text, ": ", leaf_node_dict.corp_info_arr.length, "companies")
    } else {
        console.log(leaf_node_dict.node_text, ": Empty!", )
    }
    
    // 트리 노드 선택 해제
    treeObj.deselect_node(node_id);
}

// 호출 함수
async function fnProcess(leaf_node_arr, treeObj, delay_ms_node, delay_ms_table) {
    await leaf_node_arr.reduce((prevTask, currTask) => {
        return prevTask.then(() => fnSelectNodeAndGetCorpNamesFromTableAll(
            currTask, tree, delay_ms_node, delay_ms_table));
    }, Promise.resolve());
    
    console.log('Finished');
}

console.log('Start');
fn_toggleTab("business");  // 크롤링 시각화 위해 탭 변경 (선택사항)

/* 
* Step.1 트리의 모든 최하위 노드 가져오기 
*/
var tree = $j("#businessTree").jstree(true);
top_node = tree.get_node('all');
arr_leaf_nodes = fnTreeGetLeafNodes(tree, top_node);

/*
* Step.2 모든 최하위 노드들을 순차 조회하며 테이블에서 기업 정보 가져오기
*/
fnProcess(arr_leaf_nodes, tree, 1000, 1000);
