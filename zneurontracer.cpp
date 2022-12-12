#include "zneurontracer.h"
//#include "zlocsegchain.h"
#include "swctreenode.h"
#include "c_stack.h"
#include "zswcconnector.h"
#include "tz_math.h"
#include "zvoxelarray.h"
#include "tz_stack_sampling.h"
#include "zstackbinarizer.h"
#include "tz_stack_bwmorph.h"
#include "tz_stack_math.h"
#include "tz_fimage_lib.h"
#include "tz_voxel_graphics.h"
#include "zstack.hxx"
#include "swc/zswcresampler.h"
#include "zintpoint.h"
#include "neutubeconfig.h"
#include "zstackprocessor.h"
#include "zobject3darray.h"
#include "tz_objdetect.h"
#include "zjsonobject.h"
#include "zswctree.h"
#include "swc/zswcsignalfitter.h"
#include "zneurontracerconfig.h"
#include "swc/zswcpruner.h"
#include "tz_stack_threshold.h"
#include "zerror.h"
#include <stdlib.h>
#include <string.h>
#include <iostream>

#include <stdio.h>
#include <utilities.h>
#include "utilities.h"
#include "tz_constant.h"
#include "tz_iarray.h"
#include "tz_darray.h"
#include "tz_neurotrace.h"
#include "tz_locne_chain.h"

#include "image_lib.h"
#include <stdlib.h>
#include <utilities.h>
#include "tz_error.h"
#include "tz_constant.h"
#include "tz_darray.h"
#include "tz_geo3d_scalar_field.h"
#include "tz_stack_draw.h"
#include "tz_stack_lib.h"
#include "tz_neurotrace.h"
#include "tz_locne_chain.h"

#include "tz_neurotrace.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#if defined(_WIN32) || defined(_WIN64)
  #define PCRE_STATIC
  #include <pcre2posix.h>
#else
  #include <regex.h>
#endif
#include <string.h>
#ifndef _MSC_VER
#include <dirent.h>
#else
#include "tz_dirent.h"
#endif
#include "tz_utilities.h"
#include "tz_constant.h"
#include "tz_error.h"
#define FORCE_PROGRESS
#include "tz_interface.h"
#include "tz_stack_sampling.h"
#include "tz_trace_utils.h"
#include "tz_darray.h"
#include "tz_cont_fun.h"
#include "tz_locseg_chain.h"
#include "tz_vrml_material.h"
#include "tz_vrml_io.h"
#include "tz_geo3d_utils.h"
#include "tz_string.h"
#include "tz_geo3d_point_array.h"
#include "tz_stack_graph.h"
#include "tz_image_array.h"
#include "tz_swc_cell.h"
#include "tz_u8array.h"
#include "tz_iarray.h"
#include "tz_math.h"
#include "tz_stack_attribute.h"
#include "tz_geo3d_utils.h"
#include "tz_stack_math.h"
#include "tz_workspace.h"
#include "tz_geoangle_utils.h"
#include "tz_unipointer_linked_list.h"
#include "tz_stack_utils.h"
#include "tz_int_histogram.h"
#include "tz_stack_threshold.h"
#include "private/tz_locseg_chain_p.h"
#include "private/tzp_locseg_chain.c"

#include <ctype.h>
#include <cctype>




ZNeuronTraceSeeder::ZNeuronTraceSeeder()
{
}

ZNeuronTraceSeeder::~ZNeuronTraceSeeder()
{
}

Stack* ZNeuronTraceSeeder::sortSeed(
    Geo3d_Scalar_Field *seedPointArray, const Stack *signal, Trace_Workspace *ws)
{
  Locseg_Fit_Workspace *fws = (Locseg_Fit_Workspace *) ws->fit_workspace;
  fws->sws->fs.n = 2;
  fws->sws->fs.options[0] = STACK_FIT_DOT;
  fws->sws->fs.options[1] = STACK_FIT_CORRCOEF;
  fws->pos_adjust = 1;

  m_seedArray.resize(seedPointArray->size);
  m_seedScoreArray.resize(seedPointArray->size);

  /* <seed_mask> allocated */
  Stack *seed_mask = C_Stack::make(GREY, signal->width, signal->height,
                                   signal->depth);
  Zero_Stack(seed_mask);

  RECORD_INFORMATION("************* flag1 ******************");

  QString s = QString::number(seedPointArray->size);
  std::string str_d = s.toStdString();
  RECORD_INFORMATION(str_d);

  for (int i = 0; i < seedPointArray->size; i++) {
    printf("-----------------------------> seed: %d / %d\n", i,
           seedPointArray->size);

    int index = i;
    int x = (int) seedPointArray->points[index][0];
    int y = (int) seedPointArray->points[index][1];
    int z = (int) seedPointArray->points[index][2];

    if (ws->trace_mask != NULL) {
      int v = C_Stack::value(ws->trace_mask, x, y, z);
      if (v > 0) {
        m_seedScoreArray[i] = 0;
        continue;
      }
    }

    double width = seedPointArray->values[index];

    ssize_t seed_offset = C_Stack::offset(x, y, z, signal->width, signal->height,
                                          signal->depth);

    if (width < 3.0) {
      width += 0.5;
    }
    Set_Neuroseg(&(m_seedArray[i].seg), width, 0.0, NEUROSEG_DEFAULT_H,
                 0.0, 0.0, 0.0, 0.0, 1.0);

    double cpos[3];
    cpos[0] = x;
    cpos[1] = y;
    cpos[2] = z;
    //cpos[2] /= z_scale;

    Set_Neuroseg_Position(&(m_seedArray[i]), cpos, NEUROSEG_CENTER);

    if (seed_mask->array[seed_offset] > 0) {
      printf("labeled\n");
      m_seedScoreArray[i] = 0.0;
      continue;
    }
    // RECORD_INFORMATION("************* flag2 ******************");
    //Local_Neuroseg_Optimize(locseg + i, signal, z_scale, 0);
    double z_scale = 1.0;
    Local_Neuroseg_Optimize_W(&(m_seedArray[i]), signal, z_scale, 0, fws);

    if (ws->trace_mask != NULL) {
      Local_Neuroseg &seg = m_seedArray[i];
      int v = C_Stack::value(
            ws->trace_mask,
            iround(seg.pos[0]), iround(seg.pos[1]), iround(seg.pos[2]));
      if (v > 0) {
        m_seedScoreArray[i] = 0;
        continue;
      }
    }

    m_seedScoreArray[i] = fws->sws->fs.scores[1];

    double min_score = ws->min_score;

    if (m_seedScoreArray[i] > min_score) {
      Local_Neuroseg_Label_G(&(m_seedArray[i]), seed_mask, -1, 2, z_scale);
    } else {
      Local_Neuroseg_Label_G(&(m_seedArray[i]), seed_mask, -1, 1, z_scale);
    }
  }

  /* <seed_mask> freed */
//  C_Stack::kill(seed_mask);

  return seed_mask;
}

ZNeuronConstructor::ZNeuronConstructor() : m_connWorkspace(NULL), m_signal(NULL)
{

}

ZSwcTree *ZNeuronConstructor::reconstruct(std::vector<Locseg_Chain*> &chainArray, bool conn_flag, char *filePath)
{
  ZSwcTree *tree = NULL;

  if (!chainArray.empty()) {
    int chain_number = chainArray.size();
    /* <neuronComponent> allocated */
    Neuron_Component *neuronComponent =
        Make_Neuron_Component_Array(chain_number);

    for (int i = 0; i < chain_number; i++) {
      Set_Neuron_Component(neuronComponent + i,
                           NEUROCOMP_TYPE_LOCSEG_CHAIN,
                           chainArray[i]);
    }

    /* reconstruct neuron */
    /* alloc <ns> */
    double zscale = 1.0;
    Neuron_Structure *ns;
//    if(!conn_flag)
//    {
//        ns = new_Locseg_Chain_Comp_Neurostruct(
//              neuronComponent, chain_number, m_signal, zscale, m_connWorkspace);
//    }
//    else
//    {
//        ns = Locseg_Chain_Comp_Neurostruct(
//              neuronComponent, chain_number, m_signal, zscale, m_connWorkspace);
//    }
    //不进行连接

    ns = new_Locseg_Chain_Comp_Neurostruct(
          neuronComponent, chain_number, m_signal, zscale, m_connWorkspace);

    Neuron_Structure* ns2;
    ns2 = Neuron_Structure_Locseg_Chain_To_Circle_S(ns, 1.0, 1.0);

    Neuron_Structure_To_Tree(ns2);
    // RECORD_INFORMATION("************* Neuron_Structure_To_Tree end ******************");

    tree = new ZSwcTree;
    tree->setData(Neuron_Structure_To_Swc_Tree_Circle_Z(ns2, 1.0, NULL));
    // RECORD_INFORMATION("************* Neuron_Structure_To_Swc_Tree_Circle_Z end ******************");
    tree->resortId();
    // tree->save("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/after_trace.swc");
    return tree;//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


    //连接
    ns = Locseg_Chain_Comp_Neurostruct_plus(
          neuronComponent, chain_number, m_signal, zscale, m_connWorkspace);
    // Process_Neuron_Structure(ns); // 删除冗余路径，同时也是生成最小生成树的过程
/*
    if (m_connWorkspace->crossover_test == TRUE) { // cross测试
      Neuron_Structure_Crossover_Test(ns, zscale);
    }
*/
    // 打开cross检测
    Neuron_Structure_Crossover_Test(ns, zscale);
    
    /* alloc <ns2> */
    // Neuron_Structure* ns2;
    ns2 = Neuron_Structure_Locseg_Chain_To_Circle_S(ns, 1.0, 1.0);
    Neuron_Structure_To_Tree_plus(ns2);
    tree = new ZSwcTree;
    tree->setData(Neuron_Structure_To_Swc_Tree_Circle_Z(ns2, 1.0, NULL));
    tree->resortId();
    tree->save("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/after_recons.swc");




    /* free <ns2> */
    Kill_Neuron_Structure(ns2);
    /* free <ns> */
    ns->comp = NULL;
    Kill_Neuron_Structure(ns);

    /* free <neuronComponent> */
    Clean_Neuron_Component_Array(neuronComponent, chain_number);
    free(neuronComponent);
  }

  return tree;
}



//////////////////////////ZNeuronTracer///////////////////////////////

ZNeuronTracer::ZNeuronTracer() : m_stack(NULL), m_traceWorkspace(NULL),
  m_connWorkspace(NULL), m_swcConnector(NULL),
  m_backgroundType(NeuTube::IMAGE_BACKGROUND_DARK),
  m_vertexOption(ZStackGraph::VO_ALL)
{
  init();
}

ZNeuronTracer::~ZNeuronTracer()
{
  clear();
}

void ZNeuronTracer::init()
{
  m_swcConnector = new ZSwcConnector;
  for (int i = 0; i < 3; ++i) {
    m_resolution[i] = 1.0;
//    m_stackOffset[i] = 0.0;
  }

  m_mask = NULL;
  m_baseMask = NULL;

  m_bcAdjust = false;
  m_greyFactor = 1.0;
  m_greyOffset = 0.0;
  m_preferredSignalChannel = 0;

  m_config = ZNeuronTracerConfig::getInstance();

  config();
}

void ZNeuronTracer::config()
{
//  ZNeuronTracerConfig &config = ZNeuronTracerConfig::getInstance();
  ZNeuronTracerConfig &config = m_config;

#ifdef _DEBUG_
  std::cout << "Default configuration:" << std::endl;
  config.print();
#endif


  m_seedMinScore = config.getMinSeedScore();
  m_autoTraceMinScore = config.getMinAutoScore();
  m_traceMinScore = config.getMinManualScore();
  m_2dTraceMinScore = config.getMin2dScore();
  m_usingEdgePath = config.usingEdgePath();

  m_enhancingMask = config.enhancingMask();
  m_seedingMethod = config.getSeedMethod();
  m_recover = config.getRecoverLevel();

  if (m_traceWorkspace != NULL) {
    m_traceWorkspace->refit = config.isRefit();
    m_traceWorkspace->tune_end = config.tuningEnd();
  }

  if (m_connWorkspace != NULL) {
    m_connWorkspace->sp_test = config.spTest();
    m_connWorkspace->crossover_test = config.crossoverTest();
    m_connWorkspace->dist_thre = config.getMaxEucDist();
  }
}

void ZNeuronTracer::clear()
{
  if (m_traceWorkspace != NULL) {
    if (m_traceWorkspace->fit_workspace != NULL) {
      Locseg_Fit_Workspace *fw =
          (Locseg_Fit_Workspace*) m_traceWorkspace->fit_workspace;
      fw->sws->mask = NULL;
      Kill_Locseg_Fit_Workspace(fw);
      m_traceWorkspace->fit_workspace = NULL;
    }
    Kill_Trace_Workspace(m_traceWorkspace);
    m_traceWorkspace = NULL;
  }

  if (m_connWorkspace != NULL) {
    Kill_Connection_Test_Workspace(m_connWorkspace);
    m_connWorkspace = NULL;
  }

  delete m_swcConnector;
  m_swcConnector = NULL;
  m_chainArray.clear();
  m_stack = NULL;

  clearBuffer();
}

Stack* ZNeuronTracer::getIntensityData() const
{
  Stack *stack = NULL;

  if (m_stack != NULL) {
    if (m_preferredSignalChannel < m_stack->channelNumber()) {
      stack = m_stack->c_stack(m_preferredSignalChannel);
    } else {
      stack = m_stack->c_stack();
    }
  }

  return stack;
}

void ZNeuronTracer::setIntensityField(ZStack *stack)
{
  m_stack = stack;
}

void ZNeuronTracer::setTraceRange(const ZIntCuboid &box)
{
  if (m_traceWorkspace != NULL) {
    ZIntPoint stackOffset;
    if (getStack() != NULL) {
      stackOffset = getStack()->getOffset();
    }

    m_traceWorkspace->trace_range[0] =
        box.getFirstCorner().getX() - stackOffset.getX();
    m_traceWorkspace->trace_range[3] =
        box.getLastCorner().getX() - stackOffset.getX();
    m_traceWorkspace->trace_range[1] =
        box.getFirstCorner().getY() - stackOffset.getY();
    m_traceWorkspace->trace_range[4] =
        box.getLastCorner().getY() - stackOffset.getY();
    m_traceWorkspace->trace_range[2] =
        box.getFirstCorner().getZ() - stackOffset.getZ();
    m_traceWorkspace->trace_range[5] =
        box.getLastCorner().getZ() - stackOffset.getZ();
  }
}

void ZNeuronTracer::initTraceMask(bool clearing)
{
  if (m_traceWorkspace->trace_mask == NULL) {
    m_traceWorkspace->trace_mask =
        C_Stack::make(GREY16, getStack()->width(), getStack()->height(),
                      getStack()->depth());
    clearing = true;
  }

  if (clearing) {
    Zero_Stack(m_traceWorkspace->trace_mask);
  }
}

ZSwcPath ZNeuronTracer::trace(double x, double y, double z)
{
  prepareTraceScoreThreshold(TRACING_INTERACTIVE);

  initTraceMask(false);

  Stack *stackData = getIntensityData();

  ZIntPoint stackOffset = getStack()->getOffset();

  double pos[3];
  pos[0] = x - stackOffset.getX();
  pos[1] = y - stackOffset.getY();
  pos[2] = z - stackOffset.getZ();

  /* alloc <locseg> */
  Local_Neuroseg *locseg = New_Local_Neuroseg();
  Set_Neuroseg(&(locseg->seg), 3.0, 0.0, 11.0, TZ_PI_4, 0.0, 0.0, 0.0, 1.0);

  Set_Neuroseg_Position(locseg, pos, NEUROSEG_CENTER);

  Locseg_Fit_Workspace *ws =
      (Locseg_Fit_Workspace*) m_traceWorkspace->fit_workspace;
  Local_Neuroseg_Optimize_W(locseg, stackData, 1.0, 1, ws);

  Trace_Record *tr = New_Trace_Record();
  tr->mask = ZERO_BIT_MASK;
  Trace_Record_Set_Fix_Point(tr, 0.0);
  Trace_Record_Set_Direction(tr, DL_BOTHDIR);
  /* consume <locseg> */
  Locseg_Node *p = Make_Locseg_Node(locseg, tr);

  /* alloc <locseg_chain> */
  Locseg_Chain *locseg_chain = Make_Locseg_Chain(p);

  Trace_Workspace_Set_Trace_Status(m_traceWorkspace, TRACE_NORMAL,
                                   TRACE_NORMAL);
  Trace_Locseg(stackData, 1.0, locseg_chain, m_traceWorkspace);
  Locseg_Chain_Remove_Overlap_Ends(locseg_chain);
  Locseg_Chain_Remove_Turn_Ends(locseg_chain, 1.0);

  int n;
  /* alloc <circles> */
  Geo3d_Circle *circles =
      Locseg_Chain_To_Geo3d_Circle_Array(locseg_chain, NULL, &n);

  /* free <locseg_chain> */
  Kill_Locseg_Chain(locseg_chain);

  ZSwcPath path;
  if (n > 0) {
//    bool hit = false;
    int start = 0;
    int end = n;
    if (Trace_Workspace_Mask_Value(m_traceWorkspace, circles[0].center) > 0) {
      for (int i = 1; i < n; ++i) {
        start = i - 1;
        if (Trace_Workspace_Mask_Value(m_traceWorkspace, circles[i].center) == 0) {
          break;
        }
      }
    }

    if (n > 1) {
      if (Trace_Workspace_Mask_Value(m_traceWorkspace, circles[n - 1].center) > 0) {
        for (int i = n - 2; i >= 0; --i) {
          end = i + 2;
          if (Trace_Workspace_Mask_Value(m_traceWorkspace, circles[i].center) == 0) {
            break;
          }
        }
      }
    }

    for (int i = start; i < end; ++i) {
      Swc_Tree_Node *tn = SwcTreeNode::makePointer(circles[i].center[0],
          circles[i].center[1], circles[i].center[2], circles[i].radius);
      if (!path.empty()) {
        SwcTreeNode::setParent(tn, path.back());
      }
      SwcTreeNode::translate(tn, stackOffset);
      path.push_back(tn);
    }
  }

  /* free <circles> */
  if (circles != NULL) {
    free(circles);
  }

  return path;
}

void ZNeuronTracer::updateMask(const ZSwcPath &branch)
{
  Swc_Tree_Node_Label_Workspace workspace;
  Default_Swc_Tree_Node_Label_Workspace(&workspace);
  for (ZSwcPath::const_iterator iter = branch.begin(); iter != branch.end();
       ++iter) {
    Swc_Tree_Node_Label_Stack(*iter, m_traceWorkspace->trace_mask, &workspace);
  }
}

void ZNeuronTracer::updateMask(Swc_Tree *tree)
{
  Swc_Tree_Node_Label_Workspace workspace;
  Default_Swc_Tree_Node_Label_Workspace(&workspace);
  Swc_Tree_Label_Stack(tree, m_traceWorkspace->trace_mask, &workspace);
}

void ZNeuronTracer::setTraceWorkspace(Trace_Workspace *workspace)
{
  m_traceWorkspace = workspace;
}

void ZNeuronTracer::setConnWorkspace(Connection_Test_Workspace *workspace)
{
  m_connWorkspace = workspace;
}

#define MAX_P2P_TRACE_DISTANCE 100
#define MAX_P2P_TRACE_VOLUME 1000000

Swc_Tree* ZNeuronTracer::trace(double x1, double y1, double z1, double r1,
                               double x2, double y2, double z2, double r2)
{
  prepareTraceScoreThreshold(TRACING_INTERACTIVE);

  ZIntPoint stackOffset = getStack()->getOffset();

  ZPoint targetPos(x2, y2, z2);

  x1 = iround(x1);
  y1 = iround(y1);
  z1 = iround(z1);
  x2 = iround(x2);
  y2 = iround(y2);
  z2 = iround(z2);

  x1 -= stackOffset.getX();
  y1 -= stackOffset.getY();
  z1 -= stackOffset.getZ();

  x2 -= stackOffset.getX();
  y2 -= stackOffset.getY();
  z2 -= stackOffset.getZ();

  if (x1 < 0 || y1 < 0 || z1 < 0 || x1 >= getStack()->width() ||
      y1 >= getStack()->height() || z1 >= getStack()->depth()) {
    return NULL;
  }

  ZStackGraph stackGraph;
  if (m_resolution[2] / m_resolution[0] > 3.0) {
    stackGraph.setZMargin(2);
  }
  stackGraph.updateRange(
        x1, y1, z1, x2, y2, z2,
        getStack()->width(), getStack()->height(), getStack()->depth());
  if (stackGraph.getRoiVolume() > MAX_P2P_TRACE_VOLUME) {
    return NULL;
  }

  stackGraph.setResolution(m_resolution);

  if (m_vertexOption == ZStackGraph::VO_SURFACE) {
    stackGraph.setWeightFunction(Stack_Voxel_Weight_I);
  } else {
    if (m_usingEdgePath) {
      stackGraph.setWeightFunction(Stack_Voxel_Weight_S);
    } else {
      if (m_backgroundType == NeuTube::IMAGE_BACKGROUND_BRIGHT) {
        stackGraph.setWeightFunction(Stack_Voxel_Weight_Sr);
      } else {
        stackGraph.setWeightFunction(Stack_Voxel_Weight_S);
      }
    }
  }

  ZIntCuboid box = stackGraph.getRange();
//  if (m_usingEdgePath) {
//    box.setFirstCorner(imin2(x1, x2), imin2(y1, y2), imin2(z1, z2));
//    box.setLastCorner(imax2(x1, x2), imax2(y1, y2), imax2(z1, z2));
//  }

  Stack *partial = C_Stack::crop(
        getIntensityData(), box.getFirstCorner().getX(), box.getFirstCorner().getY(),
        box.getFirstCorner().getZ(), box.getWidth(), box.getHeight(),
        box.getDepth(), NULL);

  /*
  if (m_bcAdjust) {
    Stack_Scale(partial, 0, m_greyFactor, m_greyOffset);
  }
  */

  if (m_usingEdgePath) {
    Stack *partialEdge = C_Stack::computeGradient(partial);
    C_Stack::kill(partial);
    partial = partialEdge;

#ifdef _DEBUG_2
    C_Stack::write(GET_TEST_DATA_DIR + "/test.tif", partial);
#endif
  }

  stackGraph.inferWeightParameter(partial);

  ZVoxelArray voxelArray;
  std::vector<int> path;

  if (m_usingEdgePath) {
    int x0 = box.getFirstCorner().getX();
    int y0 = box.getFirstCorner().getY();
    int z0 = box.getFirstCorner().getZ();

    int startIndex = C_Stack::indexFromCoord(
          x1 - x0, y1 - y0 , z1 - z0, C_Stack::width(partial),
          C_Stack::height(partial),
          C_Stack::depth(partial));
    int endIndex = C_Stack::indexFromCoord(
          x2 - x0, y2 - y0, z2 - z0, C_Stack::width(partial),
          C_Stack::height(partial),
          C_Stack::depth(partial));

    stackGraph.setRange(0, 0, 0, C_Stack::width(partial) - 1,
                        C_Stack::height(partial) - 1,
                        C_Stack::depth(partial) - 1);
    path = stackGraph.computeShortestPath(
          partial, startIndex, endIndex, m_vertexOption);


    for (size_t i = path.size(); i > 0; --i) {
      int x, y, z;
      C_Stack::indexToCoord(path[i - 1], C_Stack::width(partial),
          C_Stack::height(partial), &x, &y, &z);
      voxelArray.append(ZVoxel(x + x0, y + y0, z + z0));
    }

  } else {
    int width = getStack()->width();
    int height = getStack()->height();
    int depth = getStack()->depth();

    int startIndex = C_Stack::indexFromCoord(
          x1, y1, z1, width, height, depth);
    int endIndex = C_Stack::indexFromCoord(
          x2, y2, z2, width, height, depth);

    path = stackGraph.computeShortestPath(
          getIntensityData(), startIndex, endIndex, m_vertexOption);
//    C_Stack::kill(stackField);

    for (size_t i = path.size(); i > 0; --i) {
      int x, y, z;
      C_Stack::indexToCoord(path[i - 1], width, height, &x, &y, &z);
      voxelArray.append(ZVoxel(x, y, z));
    }
  }

  C_Stack::kill(partial);

  double length = voxelArray.getCurveLength();
  double dist = 0.0;

  const std::vector<ZVoxel> &voxelData = voxelArray.getInternalData();
  for (size_t i = 0; i < path.size(); ++i) {
    double ratio = dist / length;
    double r = r1 * ratio + r2 * (1 - ratio);
    voxelArray.setValue(i, r);
    if (i < path.size() - 1) {
      dist += voxelData[i].distanceTo(voxelData[i+1]);
    }
  }

  Swc_Tree *tree = voxelArray.toSwcTree();
  if (tree != NULL) {
    Swc_Tree_Translate(
          tree, stackOffset.getX(), stackOffset.getY(), stackOffset.getZ());
    ZSwcSignalFitter fitter;
    fitter.setBackground(m_backgroundType);
    fitter.setFixingTerminal(true);
    fitter.fitSignal(tree, getStack(), getSignalChannel());

    Swc_Tree_Node *leaf = tree->root;
    while (SwcTreeNode::firstChild(leaf) != NULL) {
      leaf = SwcTreeNode::firstChild(leaf);
    }
    SwcTreeNode::setPos(leaf, targetPos);
  }

  return tree;
}

Stack *ZNeuronTracer::binarize(const Stack *stack)
{
  Stack *out = C_Stack::clone(stack);
  ZStackBinarizer binarizer;

  int *histData = C_Stack::hist(stack);
  RECORD_INFORMATION("************* 0 ******************");

  ZIntHistogram hist;
  hist.setData(histData);

  RECORD_INFORMATION("************* hist.getMinValue() ******************");
  QString s = QString::number(hist.getMinValue());
  std::string str_d = s.toStdString();
  RECORD_INFORMATION(str_d);
  s = QString::number(hist.getMaxValue());
  str_d = s.toStdString();
  RECORD_INFORMATION(str_d);

  if (hist.getMinValue() == hist.getMaxValue()) {
    std::cout << "Thresholding failed" << std::endl;
    C_Stack::kill(out);
    out = NULL;
    RECORD_INFORMATION("************* 1 ******************");
  } else if (hist.getCount(hist.getMinValue()) + hist.getCount(hist.getMaxValue()) ==
             (int) C_Stack::voxelNumber(stack)) { //Only two values
    //To do: need to handle large stack
    Stack_Threshold_Binarize(out, hist.getMinValue()+50);
    QString s = QString::number(hist.getMinValue());
    std::string str_d = s.toStdString();
    RECORD_INFORMATION("************* hist.getMinValue() ******************");
    RECORD_INFORMATION(str_d);
    RECORD_INFORMATION("************* 2 ******************");
  } else {
    binarizer.setMethod(ZStackBinarizer::BM_LOCMAX);
    binarizer.setRetryCount(3);
    if (binarizer.binarize(out, -30) == false) {
      std::cout << "Thresholding failed" << std::endl;
      C_Stack::kill(out);
      out = NULL;
    }

    RECORD_INFORMATION("************* 3 ******************");
  }

  return out;
}

Stack* ZNeuronTracer::bwsolid(Stack *stack)
{
  Stack *clear_stack = NULL;

  const static int mnbr = 4;
  clear_stack = Stack_Majority_Filter_R(stack, NULL, 26, mnbr);

  Struct_Element *se = Make_Cuboid_Se(3, 3, 3);
  Stack *dilate_stack = Stack_Dilate_Fast(clear_stack, NULL, se);
  C_Stack::kill(clear_stack);
  Stack *fill_stack = dilate_stack;

  Stack *mask = Stack_Erode_Fast(fill_stack, NULL, se);
  C_Stack::kill(fill_stack);

  Kill_Struct_Element(se);

  return mask;
}

Stack* ZNeuronTracer::enhanceLine(const Stack *stack)
{
  double sigma[] = {1.0, 1.0, 1.0};
  FMatrix *result = NULL;

  if (stack->width * stack->height * stack->depth > 1024 * 1024 * 100) {
    result = El_Stack_L_F(stack, sigma, NULL);
  } else {
    result = El_Stack_F(stack, sigma, NULL);
  }

  Stack *out = Scale_Float_Stack(result->array, result->dim[0], result->dim[1],
      result->dim[2], GREY16);

  Kill_FMatrix(result);

  return out;
}


Geo3d_Scalar_Field* ZNeuronTracer::extractSeed(const Stack *mask)
{
  switch (m_seedingMethod) {
  case 1:
    return extractSeedOriginal(mask);
  case 2:
    return extractSeedSkel(mask);
  }

  return NULL;
}

Geo3d_Scalar_Field* ZNeuronTracer::extractLineSeed(
    const Stack *mask, const Stack *dist, int minObjSize)
{
  Object_3d_List *objList = Stack_Find_Object_N(
        const_cast<Stack*>(mask), NULL, 1, minObjSize, 26);
  ZObject3dArray objArray;
  objArray.append(objList);

  Geo3d_Scalar_Field *field = Make_Geo3d_Scalar_Field(objArray.size());
  for (size_t i = 0; i < objArray.size(); ++i) {
    ZObject3d *obj = objArray[i];
    ZIntPoint pt = obj->getCentralVoxel();
    field->points[i][0] = pt.getX();
    field->points[i][1] = pt.getY();
    field->points[i][2] = pt.getZ();
    field->values[i] = sqrt(
          C_Stack::value(dist, pt.getX(), pt.getY(), pt.getZ()));
  }

  return field;
}

Geo3d_Scalar_Field* ZNeuronTracer::extractSeedSkel(const Stack *mask)
{
  Stack *skel = Stack_Bwthin(mask, NULL);

  /* alloc <dist> */
  Stack *dist = Stack_Bwdist_L_U16(mask, NULL, 0);


  ZStackProcessor::RemoveBranchPoint(skel, 26);

  Stack *skel_proc = C_Stack::clone(skel);
 Geo3d_Scalar_Field *field1 = extractLineSeed(skel_proc, dist);
 C_Stack::kill(skel_proc);

 for (int i = 0; i <field1->size; ++i) {
   int x = field1->points[i][0];
   int y = field1->points[i][1];
   int z = field1->points[i][2];
   Set_Stack_Pixel(skel, x, y, z, 0, 0);
 }

#ifdef _DEBUG_2
  C_Stack::write(GET_TEST_DATA_DIR + "/test.tif", skel);
#endif


 Geo3d_Scalar_Field *field2 = extractLineSeed(skel, dist, 0);

 Geo3d_Scalar_Field *field = Geo3d_Scalar_Field_Merge(field1, field2, NULL);

 Kill_Geo3d_Scalar_Field(field1);
 Kill_Geo3d_Scalar_Field(field2);

#ifdef _DEBUG_2
  ZSwcTree tree;
  tree.forceVirtualRoot();
  for (int i = 0; i <field->size; ++i) {
    int x = field->points[i][0];
    int y = field->points[i][1];
    int z = field->points[i][2];
    double radius = field->values[i];
    SwcTreeNode::setFirstChild(
          tree.root(), SwcTreeNode::makePointer(x, y, z, radius));
  }
  tree.save(GET_TEST_DATA_DIR + "/test.swc");
#endif

  /* free <dist> */
  C_Stack::kill(dist);

  C_Stack::kill(skel);

  return field;
}

Geo3d_Scalar_Field* ZNeuronTracer::extractSeedOriginal(const Stack *mask)
{
  /* alloc <dist> */
  //is an economic version of distance transformation. It
  //* takes much less memory than Stack_Bwdist_L() does and can be much faster
  Stack *dist = Stack_Bwdist_L_U16(mask, NULL, 0);
  // Copy_Stack_Array(dist, mask);;//
  // C_Stack::write("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/dist.tif", mask);
  /* alloc <seeds> */
  Stack *seeds = Stack_Local_Max(dist, NULL, STACK_LOCMAX_CENTER);
  C_Stack::write("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/seeds.tif", mask);
  /* alloc <list> */
  Voxel_List *list = Stack_To_Voxel_List(seeds);
  /* alloc <pa> */
  Pixel_Array *pa = Voxel_List_Sampling(dist, list);
  /* free <dist> */
  C_Stack::kill(dist);
  /* alloc <voxel_array> */
  Voxel_P *voxel_array = Voxel_List_To_Array(list, 1, NULL, NULL);
  //double *pa_array = (double *) pa->array;
  uint16 *pa_array = (uint16 *) pa->array;
  printf("%d seeds found.\n", pa->size);

  QString s = QString::number(pa->size);
  std::string str_d = s.toStdString();
  RECORD_INFORMATION(str_d);
  RECORD_INFORMATION("************* pa->size ******************");

  /* alloc field */
  Geo3d_Scalar_Field *field = Make_Geo3d_Scalar_Field(pa->size);
  field->size = 0;
  int i;
  for (i = 0; i < pa->size; i++) {
    if (IS_IN_OPEN_RANGE3(voxel_array[i]->x, voxel_array[i]->y,
                          voxel_array[i]->z, 0, seeds->width - 1,
                          0, seeds->height - 1, 0, seeds->depth - 1)) {
      field->points[field->size][0] = voxel_array[i]->x;
      field->points[field->size][1] = voxel_array[i]->y;
      field->points[field->size][2] = voxel_array[i]->z;
      field->values[field->size] = sqrt((double)pa_array[i]);
      field->size++;
    }
  }

  /* free <list> */  /* free <pa> */  /* free <voxel_array> */  /* free <seeds> */
  Kill_Voxel_List(list);
  Kill_Pixel_Array(pa);
  free(voxel_array);
  C_Stack::kill(seeds);

  s = QString::number(field->size);
  str_d = s.toStdString();
  RECORD_INFORMATION(str_d);
  RECORD_INFORMATION("************* field->size ******************");
  
  return field;
}

int ZNeuronTracer::getRecoverLevel() const
{
  return m_recover;
}

void ZNeuronTracer::setRecoverLevel(int level)
{
  m_recover = level;
}

std::vector<Locseg_Chain*> ZNeuronTracer::recover(const Stack *stack)
{
  std::vector<Locseg_Chain*> chainArray;

  if (m_mask != NULL) {
    Stack *leftover = C_Stack::translate(m_mask, GREY, 0);
    Stack *traceMask = C_Stack::make(
          GREY, C_Stack::width(m_mask), C_Stack::height(m_mask),
          C_Stack::depth(m_mask));
    uint16_t *traceMaskArray =
        C_Stack::guardedArray16(m_traceWorkspace->trace_mask);
    size_t nvoxel = C_Stack::voxelNumber(m_mask);
    for (size_t i = 0; i < nvoxel; i++) {
      if ((traceMaskArray[i] > 0) || (m_baseMask->array[i] == 1)) {
        traceMask->array[i] = 1;
      } else {
        traceMask->array[i] = 0;
      }
    }

    C_Stack::kill(m_baseMask);
    m_baseMask = NULL;

    Stack *submask = Stack_Z_Dilate(traceMask, 5, stack, NULL);
    Stack_Bsub(leftover, submask, traceMask);

    C_Stack::kill(submask);
    submask = NULL;

    Stack_Remove_Small_Object(traceMask, leftover, 27, 26);
    C_Stack::translate(leftover, GREY, 1);

#ifdef _DEBUG_2
  C_Stack::write(GET_TEST_DATA_DIR + "/test.tif", leftover);
#endif

    if (Stack_Is_Dark(leftover) == FALSE) {
      double originalMinLength = m_traceWorkspace->min_chain_length;
      if (m_traceWorkspace->refit == FALSE) {
        m_traceWorkspace->min_chain_length =
            (NEUROSEG_DEFAULT_H  - 7.0) * 2.0 - 1.0; // 修改精度！！！！！！！！！！NEUROSEG_DEFAULT_H  - 1.0) * 2.0 - 1.0;
      } else {
        m_traceWorkspace->min_chain_length =
            (NEUROSEG_DEFAULT_H  - 7.0) * 1.5 - 1.0; // 修改精度！！！！！！！！！！
      }

      /* <seedPointArray> allocated */
      Geo3d_Scalar_Field *seedPointArray = extractSeed(leftover);
      C_Stack::kill(leftover);
      leftover = NULL;

      ZNeuronTraceSeeder seeder;
      prepareTraceScoreThreshold(TRACING_SEED);
      m_baseMask = seeder.sortSeed(seedPointArray, stack, m_traceWorkspace);

      /* <seedPointArray> freed */
      Kill_Geo3d_Scalar_Field(seedPointArray);

      std::vector<Local_Neuroseg>& locsegArray = seeder.getSeedArray();
      std::vector<double>& scoreArray = seeder.getScoreArray();
      chainArray = trace(stack, locsegArray, scoreArray);
      m_traceWorkspace->min_chain_length = originalMinLength;
    }
  }

  return chainArray;
}

std::vector<Locseg_Chain*> ZNeuronTracer::trace(const Stack *stack,
    std::vector<Local_Neuroseg> &locsegArray, std::vector<double> &values)
{
  prepareTraceScoreThreshold(TRACING_AUTO);

  int nchain;
  Locseg_Chain **chain =
      // Trace_Locseg_S_plus(stack, 1.0, &(locsegArray[0]), &(values[0]),
      Trace_Locseg_S(stack, 1.0, &(locsegArray[0]), &(values[0]),
      locsegArray.size(), m_traceWorkspace, &nchain);

  std::vector<Locseg_Chain*> chainArray(nchain);

  for (int i = 0; i < nchain; ++i) {
    chainArray[i] = chain[i];
  }

  free(chain);

  return chainArray;
}

void ZNeuronTracer::clearBuffer()
{
  if (m_mask != NULL) {
    C_Stack::kill(m_mask);
    m_mask = NULL;
  }

  if (m_baseMask != NULL) {
    C_Stack::kill(m_baseMask);
    m_baseMask = NULL;
  }

  m_seedDsIntv.set(0, 0, 0);
}

#if 0
std::vector<Locseg_Chain*> ZNeuronTracer::screenChain(
    const Stack *stack, std::vector<Locseg_Chain*> &chainArray)
{
  std::vector<double> scoreArray(chainArray.size(), 0.0);
  std::vector<double> intensityArray(chainArray.size(), 0.0);
  std::vector<double> lengthArray(chainArray.size(), 0.0);

  std::vector<Locseg_Chain*> goodChainArray;

  double minIntensity = Infinity;
//  double minIntensity = 0.0;
  int count = 0;

  const double scoreThreshold = 0.6;
  size_t index = 0;
  for (std::vector<Locseg_Chain*>::iterator iter = chainArray.begin();
       iter != chainArray.end(); ++iter, ++index) {
    Locseg_Chain *chain = *iter;
    scoreArray[index] = Locseg_Chain_Average_Score(
          chain, stack, 1.0, STACK_FIT_CORRCOEF);
    intensityArray[index] = Locseg_Chain_Average_Signal(chain, stack, 1.0);
    //intensityArray[index] = Locseg_Chain_Min_Seg_Signal(chain, stack, 1.0);
    if (scoreArray[index] >= 0.5) {
      minIntensity += intensityArray[index];
      ++count;
      //intensityArray[index] = Locseg_Chain_Average_Signal(chain, stack, 1.0);
      //STACK_FIT_LOW_MEAN_SIGNAL
//      if (intensityArray[index] < minIntensity) {
//        minIntensity = intensityArray[index];
//      }
    }
  }

  /*
  if (count > 0) {
    minIntensity /= count;
  }
  */

  for (index = 0; index < chainArray.size(); ++index) {
    if (scoreArray[index] >= 0.5 || intensityArray[index] >= minIntensity) {
      goodChainArray.push_back(chainArray[index]);
    } else {
      delete chainArray[index];
    }
  }

  return goodChainArray;
}
#endif

std::vector<Locseg_Chain*> ZNeuronTracer::screenChain(
    const Stack *stack, std::vector<Locseg_Chain*> &chainArray)
{
  std::vector<double> scoreArray(chainArray.size(), 0.0);
  std::vector<double> intensityArray(chainArray.size(), 0.0);
  std::vector<double> lengthArray(chainArray.size(), 0.0);

  std::vector<Locseg_Chain*> goodChainArray;

  double minIntensity = Infinity;

  const double scoreThreshold = 0.6;
  size_t index = 0;
  for (std::vector<Locseg_Chain*>::iterator iter = chainArray.begin();
       iter != chainArray.end(); ++iter, ++index) {
    Locseg_Chain *chain = *iter;
    scoreArray[index] = Locseg_Chain_Average_Score(
          chain, stack, 1.0, STACK_FIT_CORRCOEF);
    intensityArray[index] = Locseg_Chain_Average_Signal(chain, stack, 1.0);
    lengthArray[index] = Locseg_Chain_Geolen(chain);
    //intensityArray[index] = Locseg_Chain_Min_Seg_Signal(chain, stack, 1.0);
    if (scoreArray[index] >= scoreThreshold) {
      //intensityArray[index] = Locseg_Chain_Average_Signal(chain, stack, 1.0);
      //STACK_FIT_LOW_MEAN_SIGNAL
      if (intensityArray[index] < minIntensity) {
        minIntensity = intensityArray[index];
      }
    }
  }

  for (index = 0; index < chainArray.size(); ++index) {
    if (scoreArray[index] >= scoreThreshold ||
        intensityArray[index] >= minIntensity) {
      goodChainArray.push_back(chainArray[index]);
    } else {
      delete chainArray[index];
    }
  }

  return goodChainArray;
}

ZSwcTree* ZNeuronTracer::trace(const ZStack *stack, bool doResampleAfterTracing, char *filePath)
{
  ZSwcTree *tree = NULL;

  if (stack != NULL) {
    Stack *signal = C_Stack::clone(stack->c_stack(m_preferredSignalChannel));

    if (signal != NULL) {
      tree = trace(signal, doResampleAfterTracing, filePath);
      // RECORD_INFORMATION("************* 1111111111111111 ******************");
      C_Stack::kill(signal);
      if (tree != NULL) {
        tree->translate(stack->getOffset());
      }
    }
  }
  // RECORD_INFORMATION("************* 222222222222222 ******************");  
  return tree;
}

Stack* ZNeuronTracer::computeSeedMask()
{
  return computeSeedMask(getStack()->c_stack(getSignalChannel()));
}

Stack* ZNeuronTracer::computeSeedMask(Stack *stack)
{
  if (m_backgroundType == NeuTube::IMAGE_BACKGROUND_BRIGHT) {
    double maxValue = C_Stack::max(stack);
    Stack_Csub(stack, maxValue);
  }

  ZStackProcessor::SubtractBackground(stack, 0.5, 3);

  //Extract seeds
  //First mask
  std::cout << "Binarizing ..." << std::endl;

  /* <bw> allocated */
  Stack *bw = stack; //binarize(stack); //暂时删除二值化功能
  C_Stack::translate(bw, GREY, 1);

  std::cout << "Removing noise ..." << std::endl;

  /* <mask> allocated */
  Stack *mask = bwsolid(bw);

  /* <bw> freed */
  C_Stack::kill(bw);

  //Thin line mask
  /* <mask2> allocated */
  Stack *mask2 = NULL;

  if (m_enhancingMask) {
    std::cout << "Enhancing thin branches ..." << std::endl;
    mask2 = enhanceLine(stack);
  }

  if (mask2 != NULL) {
    std::cout << "Making mask for thin branches ..." << std::endl;
    ZStackBinarizer binarizer;
    binarizer.setMethod(ZStackBinarizer::BM_LOCMAX);
    binarizer.setRetryCount(5);
    binarizer.setMinObjectSize(27);

    if (binarizer.binarize(mask2) == false) {
      std::cout << "Thresholding failed" << std::endl;
      C_Stack::kill(mask2);
      mask2 = NULL;
    }
  }

  /* <mask2> freed */
  if (mask2 != NULL) {
    C_Stack::translate(mask2, GREY, 1);
    Stack_Or(mask, mask2, mask);
    C_Stack::kill(mask2);
    mask2 = NULL;
  }

  //Trace each seed
  std::cout << "Extracting seed points ..." << std::endl;

  /* <seedPointArray> allocated */
  Geo3d_Scalar_Field *seedPointArray = extractSeed(mask);

  int minSeedSize = 0;

  if (seedPointArray->size > 15000) {
    minSeedSize = 125;
  } else if (seedPointArray->size > 5000) {
    minSeedSize = 64;
  }

  if (minSeedSize > 0) {
    std::cout << "Too many seeds. Screening ..." << std::endl;
    Stack *tmpStack = C_Stack::clone(mask);
    mask = Stack_Remove_Small_Object(tmpStack, mask, minSeedSize, 26);
    C_Stack::kill(tmpStack);

    if (C_Stack::kind(mask) != GREY) {
      C_Stack::translate(mask, GREY, 1);
    }
    Kill_Geo3d_Scalar_Field(seedPointArray);
    seedPointArray = extractSeed(mask);
  }

  return mask;
}

ZSwcTree* ZNeuronTracer::trace(Stack *stack, bool doResampleAfterTracing, char *filePath)
{
  startProgress();

  ZSwcTree *tree = NULL;

  if (m_backgroundType == NeuTube::IMAGE_BACKGROUND_BRIGHT) {
    double maxValue = C_Stack::max(stack);
    Stack_Csub(stack, maxValue);
  }

  ZStackProcessor::SubtractBackground(stack, 0.5, 3);

#ifdef _DEBUG_2
  C_Stack::write(GET_TEST_DATA_DIR + "/test.tif", stack);
#endif

  //Extract seeds
  //First mask
  std::cout << "Binarizing ..." << std::endl;
  RECORD_INFORMATION("************* binarize start!!!!!!!!! ******************");

//  Find_Soma_Plus();

  /* <bw> allocated */
  Stack *bw = binarize(stack);
  C_Stack::translate(bw, GREY, 1);
//  bw->save("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/after_bin.tif");

  char after_binarize_path[500];
  memset(after_binarize_path, '\0', sizeof(after_binarize_path));
  strncpy(after_binarize_path, (char*)(filePath), strlen(filePath)-4);
  char* after_binarize_tag = "_after_binarize.tif";
  strcat(after_binarize_path, after_binarize_tag);
  C_Stack::write(after_binarize_path, bw);
  // C_Stack::write("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/after_binarize.tif", bw);

  RECORD_INFORMATION("************* binarize end!!!!!!!!! ******************");
  advanceProgress(0.05);

  std::cout << "Removing noise ..." << std::endl;
  RECORD_INFORMATION("************* Removing noise start!!!!!!!!! ******************");
  /* <mask> allocated */
  Stack *mask = bwsolid(bw);
//  mask->save("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/after_remove_noise.tif");

  char after_remove_noise_path[500];
  memset(after_remove_noise_path, '\0', sizeof(after_remove_noise_path));
  strncpy(after_remove_noise_path, (char*)(filePath), strlen(filePath)-4);
  char* after_remove_noise_tag = "_remove_noise.tif";
  strcat(after_remove_noise_path, after_remove_noise_tag);
  C_Stack::write(after_remove_noise_path, bw);
  // C_Stack::write("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/after_remove_noise.tif", mask);
  RECORD_INFORMATION("************* Removing noise end!!!!!!!!! ******************");
  advanceProgress(0.05);

  /* <bw> freed */
  C_Stack::kill(bw);

  //Thin line mask
  /* <mask2> allocated */
  Stack *mask2 = NULL;

  if (m_enhancingMask) {
    std::cout << "Enhancing thin branches ..." << std::endl;
    mask2 = enhanceLine(stack);
//    mask2->save("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/after_Enhancing.tif");
    C_Stack::write("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/after_Enhancing.tif", mask2);
    RECORD_INFORMATION("************* enhanceLine end!!!!!!!!! ******************");
    advanceProgress(0.05);
  }

  if (mask2 != NULL) {
    std::cout << "Making mask for thin branches ..." << std::endl;
    ZStackBinarizer binarizer;
    binarizer.setMethod(ZStackBinarizer::BM_LOCMAX);
    binarizer.setRetryCount(5);
    binarizer.setMinObjectSize(27);

    if (binarizer.binarize(mask2) == false) {
      std::cout << "Thresholding failed" << std::endl;
      C_Stack::kill(mask2);
      mask2 = NULL;
    }
  }

  /* <mask2> freed */
  if (mask2 != NULL) {
    C_Stack::translate(mask2, GREY, 1);
    Stack_Or(mask, mask2, mask);
    C_Stack::kill(mask2);
    mask2 = NULL;
  }
  advanceProgress(0.05);

  //Trace each seed
  std::cout << "Extracting seed points ..." << std::endl;

  /* <seedPointArray> allocated */
  RECORD_INFORMATION("************* find extractSeed start!!!!!!!!! ******************");
  // Geo3d_Scalar_Field *seedPointArray = extractSeed(mask);
  Geo3d_Scalar_Field *seedPointArray = extractSeedOriginal(mask);
  QString s1 = QString::number(seedPointArray->size);
  std::string str_d1 = s1.toStdString();
  RECORD_INFORMATION(str_d1);
  RECORD_INFORMATION("************* seedPointArray->size111!!!!!!!!! ******************");

  int minSeedSize = 0;
/*
  if (seedPointArray->size > 15000) {
    minSeedSize = 125;
  } else if (seedPointArray->size > 5000) {
    minSeedSize = 64;
  }
  */

  if (minSeedSize > 0) {
    std::cout << "Too many seeds. Screening ..." << std::endl;
    Stack *tmpStack = C_Stack::clone(mask);
    RECORD_INFORMATION("************* Remove_Small_Object start!!!!!!!!! ******************");
    mask = Stack_Remove_Small_Object(tmpStack, mask, minSeedSize, 26);
    C_Stack::write("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/after_Remove_Small_Object.tif", mask);
    RECORD_INFORMATION("************* Remove_Small_Object end!!!!!!!!! ******************");
    C_Stack::kill(tmpStack);

    if (C_Stack::kind(mask) != GREY) {
      C_Stack::translate(mask, GREY, 1);
    }
    Kill_Geo3d_Scalar_Field(seedPointArray);
    RECORD_INFORMATION("************* find extractSeed222 START!!!!!!!!! ******************");
    seedPointArray = extractSeed(mask);
    RECORD_INFORMATION("************* find extractSeed222 end!!!!!!!!! ******************");
  }

//#ifdef _DEBUG_2
//  C_Stack::write(GET_TEST_DATA_DIR + "/test.tif", mask);
//  C_Stack::write("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/test.tif", mask);
//#endif


  m_mask = mask;

  advanceProgress(0.05);

  std::cout << "Sorting seeds ..." << std::endl;
  RECORD_INFORMATION("************* seed sort start!!!!!!!!! ******************");
  ZNeuronTraceSeeder seeder;
  prepareTraceScoreThreshold(TRACING_SEED);
  RECORD_INFORMATION("************* seed sort start!!!!!!!!! ******************");
  m_baseMask = seeder.sortSeed(seedPointArray, stack, m_traceWorkspace);
  RECORD_INFORMATION("************* seed sort end!!!!!!!!! ******************");
  //C_Stack::write("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/m_baseMask.tif", m_baseMask);

  QString s = QString::number(seedPointArray->size);
  std::string str_d = s.toStdString();
  RECORD_INFORMATION(str_d);

#ifdef _DEBUG_2
  C_Stack::write(GET_TEST_DATA_DIR + "/test.tif", m_baseMask);
#endif

  advanceProgress(0.1);

  /* <seedPointArray> freed */
  Kill_Geo3d_Scalar_Field(seedPointArray);

  std::vector<Local_Neuroseg>& locsegArray = seeder.getSeedArray();
  std::vector<double>& scoreArray = seeder.getScoreArray();

  std::cout << "Tracing ..." << std::endl;
  RECORD_INFORMATION("************* tracing START!!!!!!!!! ******************");

  /* <chainArray> allocated */

    //score refer to the fit score between <locseg> and <stack>
  std::vector<Locseg_Chain*> chainArray = trace(stack, locsegArray, scoreArray);
  // 关闭recover
/*
  if (m_recover > 0) {
    std::vector<Locseg_Chain*> newChainArray = recover(stack);
    chainArray.insert(
          chainArray.end(), newChainArray.begin(), newChainArray.end());
    RECORD_INFORMATION("************* do recover ******************");
  }
  */
  advanceProgress(0.1);
/*
  if (chainArray.size() > 100) {
    std::cout << "Screening " << chainArray.size() << " tubes ..." << std::endl;
    chainArray = screenChain(stack, chainArray);
  }*/
//  chainArray = screenChain(stack, chainArray);
  advanceProgress(0.3);

  /* <mask2> freed */
//  C_Stack::kill(mask);

  std::cout << "Reconstructing ..." << std::endl;
  RECORD_INFORMATION("************* Reconstructing START!!!!!!!!! ******************");
  ZNeuronConstructor constructor;
  constructor.setWorkspace(m_connWorkspace);
  constructor.setSignal(stack);

  //Create neuron structure

  BOOL oldSpTest = m_connWorkspace->sp_test;
  /*
  if (chainArray.size() > 500) {
    std::cout << "Too many chains: " << chainArray.size() << std::endl;
    std::cout << "Turn off shortest path test" << std::endl;
    m_connWorkspace->sp_test = FALSE;
  }
  */
  // 关闭最短路测试
  m_connWorkspace->sp_test = FALSE;
  m_connWorkspace->dist_thre *= 0.3;

  /* free <chainArray> */
  tree = constructor.reconstruct(chainArray, 1, filePath);
  RECORD_INFORMATION("************* Reconstructing end!!!!!!!!! ******************");
  return tree;
//  tree->save("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/after_trace.swc");


//  tree = constructor.reconstruct(chainArray,1);
  RECORD_INFORMATION("************* ??? ******************");

  m_connWorkspace->sp_test = oldSpTest;

  advanceProgress(0.1);

  //Post process 一些剪枝过程
  if (tree != NULL) {
    // Swc_Tree_Remove_Zigzag(tree->data());
    // Swc_Tree_Tune_Branch(tree->data());
    // Swc_Tree_Remove_Spur(tree->data());
    // Swc_Tree_Merge_Close_Node(tree->data(), 0.01);
    // Swc_Tree_Remove_Overshoot(tree->data());

    if (doResampleAfterTracing) {
      ZSwcResampler resampler;
      resampler.optimalDownsample(tree);
    }

    ZSwcPruner pruner;
    pruner.setMinLength(0);
    // pruner.removeOrphanBlob(tree);

    advanceProgress(0.1);
  }

  std::cout << "Done!" << std::endl;
  endProgress();

  //tree->save("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/after_reconstruction.swc");
  return tree;
}

double ZNeuronTracer::findBestTerminalBreak(
    const ZPoint &terminalCenter, double terminalRadius,
    const ZPoint &innerCenter, double innerRadius, const Stack *stack)
{
  double d = terminalCenter.distanceTo(innerCenter);
  if (d < 0.5) {
    return 1.0;
  }

  ZPoint dvec = terminalCenter - innerCenter;
  dvec.normalize();

  double innerIntensity = Stack_Point_Sampling(
        stack, innerCenter.x(), innerCenter.y(), innerCenter.z());

  if (innerIntensity == 0.0) {
    return 1.0;
  }

  double lambda = 1.0;
  for (lambda = 1.0; lambda >= 0.3; lambda -= 0.1) {
    double radius = terminalRadius * lambda + innerRadius * (1 - lambda);
    ZPoint currentEnd = innerCenter + dvec * (d * lambda + radius);
    double terminalIntensity = Stack_Point_Sampling(
          stack, currentEnd.x(), currentEnd.y(), currentEnd.z());
    if (terminalIntensity / innerIntensity > 0.3) {
      break;
    }
  }

  return lambda;
}

void ZNeuronTracer::setMinScore(double score, ETracingMode mode)
{
  bool is2d = false;
  if (m_stack != NULL) {
    if (getStack()->depth() == 1) {
      is2d = true;
    }
  }

  if (is2d) {
    m_2dTraceMinScore = score;
  } else {
    switch (mode) {
    case TRACING_AUTO:
      m_autoTraceMinScore = score;
      break;
    case TRACING_INTERACTIVE:
      m_traceMinScore = score;
      break;
    case TRACING_SEED:
      m_seedMinScore = score;
      break;
    }
  }
}

void ZNeuronTracer::prepareTraceScoreThreshold(ETracingMode mode)
{
  bool is2d = false;
  if (m_stack != NULL) {
    if (getStack()->depth() == 1) {
      is2d = true;
    }
  }

  if (is2d) {
    m_traceWorkspace->min_score = m_2dTraceMinScore;
  } else {
    switch (mode) {
    case TRACING_AUTO:
      m_traceWorkspace->min_score = m_autoTraceMinScore;
      break;
    case TRACING_INTERACTIVE:
      m_traceWorkspace->min_score = m_traceMinScore;
      break;
    case TRACING_SEED:
      m_traceWorkspace->min_score = m_seedMinScore;
      break;
    }
  }
}

void ZNeuronTracer::initTraceWorkspace(Stack *stack)
{
  m_traceWorkspace =
      Locseg_Chain_Default_Trace_Workspace(m_traceWorkspace, stack);

  if (m_traceWorkspace->fit_workspace == NULL) {
    m_traceWorkspace->fit_workspace = New_Locseg_Fit_Workspace();
  }

  //m_traceWorkspace->min_score = 0.35;
  m_traceWorkspace->tune_end = m_config.tuningEnd();
  m_traceWorkspace->add_hit = TRUE;


  if (stack != NULL) {
    if (C_Stack::depth(stack) == 1) {
      m_traceWorkspace->min_score = m_2dTraceMinScore;
      Receptor_Fit_Workspace *rfw =
          (Receptor_Fit_Workspace*) m_traceWorkspace->fit_workspace;
      Default_R2_Rect_Fit_Workspace(rfw);
      rfw->sws->fs.n = 2;
      rfw->sws->fs.options[1] = STACK_FIT_CORRCOEF;
    }
  }
}


void ZNeuronTracer::initTraceWorkspace(ZStack *stack)
{
  if (stack == NULL || stack->channelNumber() != 1) {
    Stack *nstack = NULL;
    initTraceWorkspace(nstack);
  } else {
    initTraceWorkspace(stack->c_stack());
  }
}

void ZNeuronTracer::updateTraceWorkspaceResolution(
    double xRes, double yRes, double zRes)
{
  m_traceWorkspace->resolution[0] = xRes;
  m_traceWorkspace->resolution[1] = yRes;
  m_traceWorkspace->resolution[2] = zRes;
}

void ZNeuronTracer::updateTraceWorkspace(
    int traceEffort, bool traceMasked, double xRes, double yRes, double zRes)
{
  if (traceEffort > 0) {
    m_traceWorkspace->refit = FALSE;
  } else {
    m_traceWorkspace->refit = TRUE;
  }

  updateTraceWorkspaceResolution(xRes, yRes, zRes);

  loadTraceMask(traceMasked);
}

void ZNeuronTracer::loadTraceMask(bool traceMasked)
{
  if (traceMasked) {
    Trace_Workspace_Set_Fit_Mask(m_traceWorkspace, m_traceWorkspace->trace_mask);
  } else {
    Trace_Workspace_Set_Fit_Mask(m_traceWorkspace, NULL);
  }
}

void ZNeuronTracer::initConnectionTestWorkspace()
{
  if (m_connWorkspace == NULL) {
    m_connWorkspace = New_Connection_Test_Workspace();
    m_connWorkspace->sp_test = m_config.spTest();
    m_connWorkspace->crossover_test = m_config.crossoverTest();
  }
}

void ZNeuronTracer::updateConnectionTestWorkspace(
    double xRes, double yRes, double zRes,
    char unit, double distThre, bool spTest, bool crossoverTest)
{
  m_connWorkspace->resolution[0] = xRes;
  m_connWorkspace->resolution[1] = yRes;
  m_connWorkspace->resolution[2] = zRes;
  m_connWorkspace->unit = unit;
  m_connWorkspace->dist_thre = distThre;
  m_connWorkspace->sp_test = spTest;
  m_connWorkspace->crossover_test = crossoverTest;
}

/*
void ZNeuronTracer::setStackOffset(const ZIntPoint &pt)
{
  setStackOffset(pt.getX(), pt.getY(), pt.getZ());
}
*/

void ZNeuronTracer::setTraceLevel(int level)
{
  initTraceWorkspace(m_stack);
  initConnectionTestWorkspace();

  config();

  if (level > 0) {
    loadJsonObject(m_config.getLevelJson(level));
  }

#if 0
  if (m_traceWorkspace == NULL) {
    initTraceWorkspace(m_stack);
  }

  if (m_connWorkspace == NULL) {
    initConnectionTestWorkspace();
  }

//  m_traceWorkspace->tune_end = FALSE;
  m_traceWorkspace->refit = FALSE;
  m_connWorkspace->sp_test = FALSE;
  m_connWorkspace->crossover_test = FALSE;
  m_traceWorkspace->tune_end = TRUE;
  m_enhancingMask = false;
  m_seedingMethod = 1;
  m_recover = 0;

  if (level >= 2) {
    m_seedingMethod = 2;
  }

  if (level >= 3) {
    m_connWorkspace->sp_test = TRUE;
  }

  if (level >= 4) {
    m_enhancingMask = true;
  }

  if (level >= 5) {
    m_recover = 1;
  }

  if (level >= 6) {
    m_traceWorkspace->refit = TRUE;
  }
#endif
}

/*
const char *ZNeuronTracer::m_levelKey = "level";
const char *ZNeuronTracer::m_minimalScoreKey = "minimalScore";
const char *ZNeuronTracer::m_minimalSeedScoreKey = "minimalSeedScore";
const char *ZNeuronTracer::m_spTestKey = "spTest";
const char *ZNeuronTracer::m_enhanceLineKey = "enhanceLine";
*/
void ZNeuronTracer::loadJsonObject(const ZJsonObject &obj)
{
#ifdef _DEBUG_
  obj.print();
#endif

  const char *key = ZNeuronTracerConfig::getLevelKey();
  if (obj.hasKey(key)) {
    setTraceLevel(ZJsonParser::integerValue(obj[key]));
  }

  key = ZNeuronTracerConfig::getMinimalManualScoreKey();
  if (obj.hasKey(key)) {
    m_traceMinScore = ZJsonParser::numberValue(obj[key]);
  }

  key = ZNeuronTracerConfig::getMinimalSeedScoreKey();
  if (obj.hasKey(key)) {
    m_seedMinScore = ZJsonParser::numberValue(obj[key]);
  }

  key = ZNeuronTracerConfig::getSpTestKey();
  if (obj.hasKey(key)) {
    m_connWorkspace->sp_test = ZJsonParser::booleanValue(obj[key]);
  }

  key = ZNeuronTracerConfig::getEnhanceLineKey();
  if (obj.hasKey(key)) {
    m_enhancingMask = ZJsonParser::booleanValue(obj[key]);
  }

  key = ZNeuronTracerConfig::getRefitKey();
  if (obj.hasKey(key)) {
    m_traceWorkspace->refit = ZJsonParser::booleanValue(obj[key]);
  }

  key = ZNeuronTracerConfig::getSeedMethodKey();
  if (obj.hasKey(key)) {
    m_seedingMethod = ZJsonParser::integerValue(obj[key]);
  }

  key = ZNeuronTracerConfig::getRecoverKey();
  if (obj.hasKey(key)) {
    m_recover = ZJsonParser::integerValue(obj[key]);
  }

  key = ZNeuronTracerConfig::getCrossoverTestKey();
  if (obj.hasKey(key)) {
    m_connWorkspace->crossover_test = ZJsonParser::booleanValue(obj[key]);
  }

  key = ZNeuronTracerConfig::getTuneEndKey();
  if (obj.hasKey(key)) {
    m_traceWorkspace->tune_end = ZJsonParser::booleanValue(obj[key]);
  }

  key = ZNeuronTracerConfig::getEdgePathKey();
  if (obj.hasKey(key)) {
    m_usingEdgePath = ZJsonParser::booleanValue(obj[key]);
  }
}

void ZNeuronTracer::test()
{
#if 1
  ZStack stack;
//  stack.load(GET_TEST_DATA_DIR + "/benchmark/crash/Binary.tif");

  stack.load("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/example.tif");
  Stack *out = binarize(stack.c_stack());
//  setIntensityField(&signal);

//    int level = 0;
//    tracer.setTraceLevel(level);

//    ZSwcTree *tree = trace(&signal);
//    tree->save("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/test.swc");

//  C_Stack::write(GET_TEST_DATA_DIR + "/test.tif", out);
  C_Stack::write("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/test.tif", out);
#endif
}

Neuron_Structure*
new_Locseg_Chain_Comp_Neurostruct(Neuron_Component *comp, int n,
                  const Stack *stack, double z_scale,
                  void *ws)
{
  Neuron_Structure *ns = New_Neuron_Structure();
  Neuron_Structure_Set_Component_Array(ns, comp, n);

//  int i, j;

//  Graph_Workspace *gw = New_Graph_Workspace();

//  for (i = 0; i < n; i++) {

//    for (j = 0; j < n; j++) {
//      if (i != j) {
//        Neurocomp_Conn conn;
//        conn.mode = NEUROCOMP_CONN_HL;
//        Locseg_Chain *chain_i = NEUROCOMP_LOCSEG_CHAIN(comp+ i);
//        Locseg_Chain *chain_j = NEUROCOMP_LOCSEG_CHAIN(comp + j);

//        if (Locseg_Chain_Connection_Test(chain_i, chain_j, stack,
//                         z_scale, &conn, (Connection_Test_Workspace*)ws) == TRUE) {
//          Neurocomp_Conn_Translate_Mode(Locseg_Chain_Length(chain_j),&conn);
//        }
//      }
//    }

//  }



//  Kill_Graph_Workspace(gw);

  return ns;
}

Neuron_Structure*
Locseg_Chain_Comp_Neurostruct_plus(Neuron_Component *comp, int n,
                  const Stack *stack, double z_scale,
                  void *ws)
{
  Neuron_Structure *ns = New_Neuron_Structure();
  Neuron_Structure_Set_Component_Array(ns, comp, n);

  int i, j;

  Graph_Workspace *gw = New_Graph_Workspace();


  for (i = 0; i < n; i++) {
    for (j = 0; j < n; j++) {
      if (i != j) {
        Neurocomp_Conn conn;
        conn.mode = NEUROCOMP_CONN_HL;
        Locseg_Chain *chain_i = NEUROCOMP_LOCSEG_CHAIN(comp + i);
        Locseg_Chain *chain_j = NEUROCOMP_LOCSEG_CHAIN(comp + j);

        if (Locseg_Chain_Connection_Test_Plus(chain_i, chain_j, stack,
                         z_scale, &conn, (Connection_Test_Workspace*)ws) == TRUE) { // 计算连接性，如果能连接则将路径信息存在conn中
          Neurocomp_Conn_Translate_Mode(Locseg_Chain_Length(chain_j),
                        &conn);
          BOOL conn_existed = FALSE;

          // if(i == 0 && conn.info[0] == 0)
          //   conn.cost = -1;

          if (i > j) { // 第二次判断两节点的连接情况
            if (ns->graph->nedge > 0) { // 存在路径
              int edge_idx = Graph_Edge_Index(j, i, gw);
              if (edge_idx >= 0) { // 之前计算出过路径
                  if (conn.mode == NEUROCOMP_CONN_LINK && ns->conn[edge_idx].info[0] == conn.info[1]) {  // info[0]01表示连头还是尾，info[1]表示连接的第几个节点
                    conn_existed = TRUE;
                  } else if (ns->conn[edge_idx].mode == NEUROCOMP_CONN_LINK && ns->conn[edge_idx].info[1] == conn.info[0]) {
                    conn_existed = TRUE;
                  }
                  if (conn_existed == TRUE && ns->conn[edge_idx].cost > conn.cost) {  //更新路径
                    Neurocomp_Conn_Copy(ns->conn + edge_idx, &conn);
                    ns->graph->edges[edge_idx][0] = i; // 这里是保存最短路径
                    ns->graph->edges[edge_idx][1] = j;
                    Graph_Update_Edge_Table(ns->graph, gw);
                  }
              }
            }
          }

          if (conn_existed == FALSE) {
            
            Neuron_Structure_Add_Conn(ns, i, j, &conn);
            Graph_Expand_Edge_Table(i, j, ns->graph->nedge - 1, gw);
          }
        }
      }
    }
  }
  Kill_Graph_Workspace(gw);

  return ns;
}

BOOL Locseg_Chain_Connection_Test_Plus(Locseg_Chain *chain1, Locseg_Chain *chain2,
				  const Stack *stack, double z_scale, 
				  Neurocomp_Conn *conn, 
				  Connection_Test_Workspace *ctw)
{
  conn->info[0] = -1;
  conn->cost = 100000;
  TZ_ASSERT(ctw != NULL, "Null workspace");

  /* No connection if either of the chains is empty. */
  if (Locseg_Chain_Is_Empty(chain1) || Locseg_Chain_Is_Empty(chain2)) {
    conn->mode = NEUROCOMP_CONN_NONE;
    return FALSE;
  }

  /* Initialize resolution */
  double res[3] = {1.0, 1.0, 1.0};
  darraycpy(res, ctw->resolution, 0, 3);

  double xz_ratio = 1.0;
  
  if (res[0] != res[2]) {
    xz_ratio = res[0] / res[2];
  }

  /* Get head and tail of the hook */
  Local_Neuroseg *shead = Locseg_Chain_Head_Seg(chain1);
  Local_Neuroseg *stail = Locseg_Chain_Tail_Seg(chain1);
  Local_Neuroseg *head = Copy_Local_Neuroseg(shead);
  Local_Neuroseg *tail = Copy_Local_Neuroseg(stail);
  /* Adjust head and tail */
  Flip_Local_Neuroseg(tail);

  if (Locseg_Chain_Length(chain1) >= 1) {
    head->seg.h = 2.0;
    tail->seg.h = 2.0;
  }

  Local_Neuroseg_Scale_Z(head, xz_ratio);
  Local_Neuroseg_Scale_Z(tail, xz_ratio);
  
  // /* get upper bound */ 
  // 距离上限：hook指chain1，hook的头或尾到loop的最大距离？？
  int index = 0;

  Geo3d_Ball range1, range2;
  Local_Neuroseg *locseg;

  double dist2soma = 0.0;
  double mindist = 100000;
/*
  if (ctw->hook_spot == 0) {
    mindist = locseg_chain_dist_upper_bound(chain2, xz_ratio, head);
  }

  if (ctw->hook_spot == 1) {
    mindist = locseg_chain_dist_upper_bound(chain2, xz_ratio, tail);
  }
  
  if (ctw->hook_spot == -1) {
    mindist = dmin2(locseg_chain_dist_upper_bound(chain2, xz_ratio, head),
		    locseg_chain_dist_upper_bound(chain2, xz_ratio, tail));
  }
*/
  // mindist = dmin2(locseg_chain_dist_upper_bound(chain2, xz_ratio, head),
	// 	    locseg_chain_dist_upper_bound(chain2, xz_ratio, tail));

  Locseg_Chain_Iterator_Start(chain2, DL_HEAD);

  //Local_Neuroseg *source_seg = NULL;
  //Local_Neuroseg *target_seg = NULL;

  double tmp_pos[3];

  conn->mode = NEUROCOMP_CONN_HL;
  Local_Neuroseg *locseg2 = New_Local_Neuroseg();

  /* Calculate the distance from the hook end(s) to the loop chain surface. */
  while ((locseg = Locseg_Chain_Next_Seg(chain2)) != NULL) { // head、tail是chain1，locseg是chain2中的内容，信息放在range1里
    Local_Neuroseg_Copy(locseg2, locseg);
    Local_Neuroseg_Scale_Z(locseg2, xz_ratio);    
    Local_Neuroseg_Ball_Bound(locseg2, &(range1));

    /* if the head is required to be tested */
    if ((ctw->hook_spot == 0) || (ctw->hook_spot == -1)){
      Local_Neuroseg_Ball_Bound(head, &(range2));
      /* Ignore it if the minimal possible distance is not less than 
       * the current minial distnace */
      if (Geo3d_Dist(range1.center[0], range1.center[1], range1.center[2], 
		      range2.center[0], range2.center[1], range2.center[2]) - 
          range1.r - range2.r < mindist) {	
        double dist = Local_Neuroseg_Dist2(head, locseg2, tmp_pos);
        BOOL update = FALSE;
        if (dist < mindist) {
          mindist = dist;
          conn->pdist = Local_Neuroseg_Planar_Dist_L(head, locseg2);
          update = TRUE;
        } else if (dist == mindist) {
          double pdist = Local_Neuroseg_Planar_Dist_L(head, locseg2);
          if (conn->pdist > pdist) {	    
            conn->pdist = pdist;
            update = TRUE;
          }
        }

        if (update) {
          conn->info[0] = 0;
          conn->info[1] = index;
          conn->pos[0] = tmp_pos[0];
          conn->pos[1] = tmp_pos[1];
          conn->pos[2] = tmp_pos[2];
          //source_seg = shead;
          //target_seg = locseg;
          dist2soma = Geo3d_Dist(256, 256, 128, tmp_pos[0], tmp_pos[1], tmp_pos[2]);
        }
      }
    }

    /* if the tail is required to be tested */
    if ((ctw->hook_spot == 1) || (ctw->hook_spot == -1)){
      Local_Neuroseg_Ball_Bound(tail, &(range2));
      /* Ignore it if the minimal possible distance is not less than 
       * the current minial distnace */      
      if (Geo3d_Dist(range1.center[0], range1.center[1], range1.center[2], 
		      range2.center[0], range2.center[1], range2.center[2])
	        - range1.r - range2.r < mindist) {
        double dist = Local_Neuroseg_Dist2(tail, locseg2, tmp_pos);
        if (dist < mindist) {
          mindist = dist;
          conn->info[0] = 1;
          conn->info[1] = index;
          conn->pos[0] = tmp_pos[0];
          conn->pos[1] = tmp_pos[1];
          conn->pos[2] = tmp_pos[2];
          dist2soma = Geo3d_Dist(256, 256, 128, tmp_pos[0], tmp_pos[1], tmp_pos[2]);
          conn->pdist = Local_Neuroseg_Planar_Dist_L(tail, locseg2);
          //source_seg = stail;
          //target_seg = locseg;
        } else if (dist == mindist) {
          double pdist = Local_Neuroseg_Planar_Dist_L(tail, locseg2);
          if (conn->pdist > pdist) {
            conn->info[0] = 1;
            conn->info[1] = index;
            conn->pos[0] = tmp_pos[0];
            conn->pos[1] = tmp_pos[1];
            conn->pos[2] = tmp_pos[2];
            dist2soma = Geo3d_Dist(256, 256, 128, tmp_pos[0], tmp_pos[1], tmp_pos[2]);
            conn->pdist = pdist;
            //source_seg = stail;
            //target_seg = locseg;
          }
        }
      }
    }

    index++;
  }

  Delete_Local_Neuroseg(locseg2);

  /* scale position back to the chain space */
  conn->pos[2] *= xz_ratio;

  /* free <head> */
  Delete_Local_Neuroseg(head);  
  /* free <tail> */
  Delete_Local_Neuroseg(tail);  

  /*
  double dist_thre = 20.0;
  double big_euc = 15.0;
  double big_planar = 10.0;

  double dist_thre = ctw->dist_thre;
  double big_euc = ctw->big_euc;
  double big_planar = ctw->big_planar;
  */

  conn->sdist = mindist;

#ifdef _DEBUG_2
  if ((Geo3d_Dist(conn->pos[0], conn->pos[1], conn->pos[2], 370, 163, 20)
       < 5.0) && (conn->sdist < 5.0)) {
    printf("Debug here.\n");
  }
#endif

  //if ((conn->sdist > (ctw->dist_thre)) /*||  ((conn->sdist > big_euc) && (conn->pdist > big_planar))*/) 
  // if ((dist2soma <= 10 && conn->sdist > ctw->dist_thre * 2.0) ||
  //     (dist2soma > 10 && conn->sdist > ctw->dist_thre)) // 优化soma附近的连接
  if (conn->sdist > ctw->dist_thre)
  {
    conn->mode = NEUROCOMP_CONN_NONE;
    //conn->cost = 10.0; // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    conn->cost = 100000.0;
    return FALSE;
  } 
  else 
  {
    Local_Neuroseg *locseg1 = NULL;
    double test_pos[3];

    if (conn->info[0] == 0)// 连接头 
    { 
      locseg1 = Locseg_Chain_Head_Seg(chain1);
      Local_Neuroseg_Top(locseg1, test_pos);
    } 
    else // 连接尾
    {
      locseg1 = Locseg_Chain_Tail_Seg(chain1);
      Local_Neuroseg_Bottom(locseg1, test_pos);
    }

    // 取向？
    Geo3d_Orientation_Normal(locseg1->seg.theta, locseg1->seg.psi,
			     conn->ort, conn->ort + 1, conn->ort + 2);

    /*    
    if ((conn->sdist > 5.0) && (conn->pos != NULL)) {
      double test_vec[3];
      if (conn->info[0] == 0) {
	test_vec[0] = -conn->pos[0] + test_pos[0];
	test_vec[1] = -conn->pos[1] + test_pos[1];
	test_vec[2] = -conn->pos[2] + test_pos[2];
      } else {
	test_vec[0] = conn->pos[0] - test_pos[0];
	test_vec[1] = conn->pos[1] - test_pos[1];
	test_vec[2] = conn->pos[2] - test_pos[2];	
      }
      if (Geo3d_Dot_Product(test_vec[0], test_vec[1], test_vec[2],
			    conn->ort[0], conn->ort[1], conn->ort[2]) < 0.0) {
	conn->mode = NEUROCOMP_CONN_NONE;
	conn->cost = 10.0;
	return FALSE;	
      }
    }
        */

    //locseg2 = Locseg_Chain_Peek_Seg_At(chain2, conn->info[1]);
    
    //int n;
    //double *feat = Locseg_Conn_Feature(locseg1, locseg2, NULL, res, NULL, &n);

    /*
    conn->cost = 
      1.0 / (1.0 + exp(0.546599 * feat[0] + -1.45673 * feat[7] +
		       6.48994 * fabs((feat[4] - feat[5])/(feat[4] + feat[5])) +
		       0.433958 * fabs(feat[6])));     
    */
    /*
    conn->cost = 
      1.0 / (1.0 + exp(0.592935 * feat[0] + -1.27852 * feat[7] +
		       0.766847 * fabs(feat[6])));
    */

    // 最短路测试？
    if (0 && (conn->sdist > 2.0) && (ctw->sp_test == TRUE) && (stack != NULL)){
      double gdist = 0.0;
      Stack_Graph_Workspace *sgw = New_Stack_Graph_Workspace();
      sgw->conn = 26;
      sgw->wf = Stack_Voxel_Weight_S;
      sgw->resolution[0] = ctw->resolution[0];
      sgw->resolution[1] = ctw->resolution[1];
      sgw->resolution[2] = ctw->resolution[2];
      //sgw->argv[3] = Locseg_Chain_Min_Seg_Signal(chain1, stack, z_scale);
      //		   Locseg_Chain_Min_Seg_Signal(chain2, stack, z_scale));

      sgw->signal_mask = ctw->mask;
      sgw->including_signal_border = TRUE;
      Int_Arraylist *path = Locseg_Chain_Shortest_Path(chain1, chain2,
						       stack, z_scale, sgw);
      sgw->signal_mask = NULL;

      if (path != NULL) 
      {
	gdist = sgw->value;
	double path_dist = path_length(path, stack->width, stack->height,
	    ctw->resolution[2] / ctw->resolution[1]);
	UNUSED_PARAMETER(path_dist);
	int coord[3];
	int hit_index;

	if (path->length >= 5) {
	  int k;
	  int dark_count = 0;
	  int bright_count = 0;
	  hit_index = 0;
	  for (k = 0; k < path->length; k++) {
	    if (hit_index < 3) {
	      Stack_Util_Coord(path->array[k], stack->width, 
			       stack->height, coord, coord + 1,
			       coord + 2);
	      if (conn->info[0] == 0) {
		hit_index = Locseg_Chain_Hit_Test(chain1, DL_FORWARD,
						  coord[0], coord[1], coord[2]);
	      } else {
		hit_index = Locseg_Chain_Hit_Test(chain1, DL_BACKWARD,
						  coord[0], coord[1], coord[2]);
	      }
	    }
	    
	    BOOL count = TRUE;
	    if (ctw->mask != NULL) {
	      if (Stack_Array_Value(ctw->mask, path->array[k]) < 0.5) {
		count = FALSE;
	      }
	    }
	    
	    if (count) {
	      if ((Stack_Array_Value(stack, path->array[k]) < 
		   sgw->argv[3] - sgw->argv[4]) || 
		  (Stack_Array_Value(stack, path->array[k]) == 0)){
		dark_count++;
	      } else {
		bright_count++;
	      }
	    }
	  }
	  
	  /* ~w~ */
	  if (((dark_count >= 2) && (dark_count >= bright_count)) || 
	      (dark_count >= 5) || (hit_index >= 3) /*|| 
	      (path_dist > dist_thre * 3.0)*/) {
	    conn->mode = NEUROCOMP_CONN_NONE;
	  } else {
	    if (dark_count + bright_count >= 2) {
	      int prev_pos[3];
	      int pos[3];
	      Stack_Util_Coord(path->array[path->length-2], stack->width, 
			       stack->height, prev_pos, prev_pos + 1,
			       prev_pos + 2);
	      int count = 0;
	      int i;
	      conn->ort[0] = 0.0;
	      conn->ort[1] = 0.0;
	      conn->ort[2] = 0.0;
	      for (i = path->length - 3; i >= 0; i--) {
          Stack_Util_Coord(path->array[i], stack->width, 
              stack->height, pos, pos + 1, pos + 2);
          conn->ort[0] += prev_pos[0] - pos[0];
          conn->ort[1] += prev_pos[1] - pos[1];
          conn->ort[2] += prev_pos[2] - pos[2];
          prev_pos[0] = pos[0];
          prev_pos[1] = pos[1];
          prev_pos[2] = pos[2];
          count++;
          if (count >= 5) {
            break;
          }
	      }

	      Coordinate_3d_Unitize(conn->ort);
	    }
	  }
	}

	if (sgw->resolution != NULL) {
	  gdist /= sgw->resolution[0];
	}
      } else {
        conn->mode = NEUROCOMP_CONN_NONE;
        gdist = 0.0;
      }
      
      Kill_Stack_Graph_Workspace(sgw);

      /*
      Path_Test_Workspace ptw;
      default_path_test_workspace(&ptw);
      ptw.z_res = ctw->resolution[2] / ctw->resolution[0];

      if (!is_path_valid(stack, path->array, path->length, &ptw)) {
	conn->mode = NEUROCOMP_CONN_NONE;
      }
      */

#ifdef _DEBUG_
      printf("%g, %g, %g\n", conn->pos[0], conn->pos[1], conn->pos[2]);
      printf("%g, %g, %g\n", conn->ort[0], conn->ort[1], conn->ort[2]);
#endif
      
      if (path != NULL) {
	      Kill_Int_Arraylist(path);
      }
      conn->cost = 1.0 / (1.0 + exp(-(conn->sdist + gdist)/100.0));
      //conn->cost = 1.0 / (1.0 + exp(-conn->sdist));
    } else {
      // conn->cost = 1.0 / (1.0 + exp(-conn->sdist / 100.0));
      // conn->cost = conn->sdist * 100;
    }
    
    
    //conn->cost = 1.0 / (1.0 + exp(-feat[7]));

    /*
    conn->cost = 
      1.0 / (1.0 + exp(0.546474 * feat[0] -1.45891 * feat[7] +
		       6.50761 * fabs((feat[4] - feat[5])/(feat[4] + feat[5])) +
		       0.433692 * fabs(feat[6])));
    */

    /*
    conn->cost = exp(-0.559668 * feat[0] + 1.55163 * feat[7] +
		     -7.01974 * fabs((feat[4] - feat[5])/(feat[4] + feat[5])) +
		     -0.470092 * fabs(feat[6]));
    */

    /*
    conn->cost = exp(-1.02326 * feat[0] + 1.0818 * feat[7] +
		     0.0695292 * fabs(feat[0] * feat[7]));
    */
    /*
    conn->cost = exp(-0.7429 * feat[0] + 0.405817 * feat[7] +
		     0.173818 * feat[0] * feat[7]);
    */

    /*
    conn->cost = exp(0.0189185 * feat[0] + 0.880418 * feat[7] +
		     -6.06658 * fabs((feat[4] - feat[5])/(feat[4] + feat[5])) +
		     -0.42791 * fabs(feat[6]));
    */

/*
    //conn->cost = exp(-0.276669 * feat[0] + 0.621916 * feat[7]);

    //conn->cost = exp(-0.605281 * feat[0] + 1.37511 * feat[7] -0.838392 * fabs(feat[6]));
    
    //conn->cost = feat[7];

    //conn->cost = exp(-(0.6053 * feat[0] -1.3751 * feat[7] + 0.8384 * fabs(feat[6])));

    //conn->cost = exp(-(1.1812 * feat[0] - 2.5651 * feat[7] + 0.6728 * fabs(feat[6])));

    //conn->cost = feat[0] + feat[6];

    //conn->cost = feat[2] + feat[7];

    //conn->cost = feat[3] + feat[10];
    //free(feat);


    //conn->cost = mindist * res[0] + conn->cost;
    */
  }
/****判断是连接头、尾还是连接中间*****/
  if (conn->mode == NEUROCOMP_CONN_NONE) {
    return FALSE;
  } 
  else 
  {
    conn->cost = (conn->sdist + dist2soma) * 100 ;
    if (ctw->interpolate == TRUE) {
      if (conn->mode == NEUROCOMP_CONN_HL) // 连接中间
      {
        int index = Locseg_Chain_Interpolate_L(chain2, conn->pos, conn->ort, 
                      conn->pos);
        if (index >= 0) 
        {
          conn->cost *= 1.0; 
          conn->info[1] = index;
        } 
        else 
        {
          // 鼓励NEUROCOMP_CONN_LINK 这种情况，即鼓励head/tail to head/tail这种连接
          // conn->cost *= 0.5; 
          if (conn->info[1] == 0)  // 连接头
          {
            conn->mode = NEUROCOMP_CONN_LINK;
            conn->info[1] = 0;
          } 
          else if (conn->info[1] == Locseg_Chain_Length(chain2) - 1) // 连接尾
          {
            conn->mode = NEUROCOMP_CONN_LINK;
            conn->info[1] = 1;	  
          }
        }
        // 需要适当的比soma的半径大一些
        // if(dist2soma <= 10)
        //   conn->cost *= 0.01;
      }
    }
    return TRUE;
  }
}



void Find_Soma_Plus()
{

  Geo3d_Scalar_Field *seed = Read_Geo3d_Scalar_Field("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/example.tif");

  int *indices = iarray_malloc(seed->size);
  double *values = darray_malloc(seed->size);

  int i;
  for (i = 0; i < seed->size; i++) {
    indices[i] = i;
  }

  darraycpy(values, seed->values, 0, seed->size);

  darray_qsort(values, indices, seed->size);

  int index = indices[seed->size-1];

  double r = seed->values[index];

  Local_Neuroseg_Ellipse *segs[10];



//  Stack *stack;
//  char *tem_path ="C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/example.tif";
//  stack = Read_Stack(tem_path);
    Stack *stack = C_Stack::readSc("C://Users/12626/Desktop/seu-allen/neuTube_win64.2018.07.12/neutube_ws/example.tif");

//  Locne_Chain *somas[10];
//  int nsoma = 0;

//  /*
//  segs[0] = New_Local_Neuroseg_Ellipse();
//  Set_Local_Neuroseg_Ellipse(segs[0], r, r, TZ_PI_2, 0, 0, 0,
//                 seed->points[index][0],
//                 seed->points[index][1],
//                 seed->points[index][2]);

//  somas[nsoma++] = Trace_Soma(stack, 1.0, segs[0], NULL);
//  */

//  int j;
//  double soma_r, tube_r;
//  double max_r;
//  soma_r = -1.0;

//  for (i = seed->size - 1; i >= 0; i--) {
//    BOOL traced = FALSE;
//    for (j = 0; j < nsoma; j++) {
//      if (Locne_Chain_Hittest(somas[j], seed->points[indices[i]]) == TRUE) {
//        traced = TRUE;
//        Print_Coordinate_3d(seed->points[indices[i]]);
//        break;
//      }
//    }

//    if (traced == FALSE) {
//      index = indices[i];

//      tube_r = seed->values[index];
//      segs[nsoma] = New_Local_Neuroseg_Ellipse();
//      Set_Local_Neuroseg_Ellipse(segs[nsoma],
//                 r, r, TZ_PI_2, 0, 0, 0, 0,
//                 seed->points[index][0],
//                 seed->points[index][1],
//                 seed->points[index][2]);

///*
//void Set_Local_Neuroseg_Ellipse(Local_Neuroseg_Ellipse *locne,
//                double rx, double ry, double theta, double psi,
//                double alpha,
//                double offset_x, double offset_y,
//                double x, double y, double z);
//*/

//      somas[nsoma] = Trace_Soma(stack, 1.0, segs[nsoma], NULL);

//      if ((Soma_Score(somas[nsoma]) < 1.5) || (nsoma >= 9)
//      || (Locne_Chain_Length(somas[nsoma]) < 5)) {
//        //	sprintf(file_path, "%s/%s.bn", dir, "max_r");
//            if (soma_r < 0.0) {
//              max_r = tube_r * 1.5;
//            } else {
//              max_r = (tube_r + soma_r) / 2.0;
//            }
//        //	darray_write(file_path, &max_r, 1);
//            break;
//      } else {
//            soma_r = tube_r;
//      }

//      nsoma++;
//    }
//  }

//  printf("%d soma found.\n", nsoma);

//  QString s = QString::number(nsoma);
//  std::string str_d = s.toStdString();
//  RECORD_INFORMATION("********************find soma");
//  RECORD_INFORMATION(str_d);

////  for (i = 0; i < nsoma; i++) {
////    Print_Local_Neuroseg_Ellipse(segs[i]);
////    printf("soma score: %g\n", Soma_Score(somas[i]));
////    sprintf(file_path, "%s/%s%d.bn", dir, Get_String_Arg("-o"), i);
////    Write_Locne_Chain(file_path, somas[i]);
////  }

////  if (Is_Arg_Matched("-mask")) {
////    Stack *trace_mask = Make_Stack(GREY16,
////				   stack->width, stack->height, stack->depth);
////    Zero_Stack(trace_mask);
////    for (i = 0; i < nsoma; i++) {
////      Soma_Stack_Mask(somas[i], trace_mask, 1.0, i + 1);
////    }
////    sprintf(file_path, "%s/%s", dir, Get_String_Arg("-mask"));
////    Write_Stack(file_path, trace_mask);

////    printf("%s created", file_path);
////  }

////  return 0;
}

static double 
locseg_chain_dist_upper_bound(Locseg_Chain *chain, double z_scale,
			      Local_Neuroseg *testseg)
{
  double source[3];
  Local_Neuroseg_Center(testseg, source);

  double target[3];
  double dist;
  double min_dist;
  
  Locseg_Chain_Iterator_Start(chain, DL_HEAD);
  Local_Neuroseg *locseg2 = New_Local_Neuroseg();

  Local_Neuroseg_Copy(locseg2, Locseg_Chain_Next_Seg(chain));

  Local_Neuroseg_Scale_Z(locseg2, z_scale);

  Local_Neuroseg_Center(locseg2, target);
  min_dist = Geo3d_Dist(source[0], source[1], source[2], 
			target[0], target[1], target[2]);

  Local_Neuroseg *locseg = NULL;
  while ((locseg = Locseg_Chain_Next_Seg(chain)) != NULL) {
    Local_Neuroseg_Copy(locseg2, locseg);
    Local_Neuroseg_Scale_Z(locseg2, z_scale);

    Local_Neuroseg_Center(locseg2, target);
    dist = Geo3d_Dist(source[0], source[1], source[2], 
		      target[0], target[1], target[2]);

    if (dist < min_dist) {
      min_dist = dist;
    }
  }

  Delete_Local_Neuroseg(locseg2);

  return min_dist;
}

void Neuron_Structure_To_Tree_plus(Neuron_Structure *ns)
{
  // (NEUROCOMP_GEO3D_CIRCLE(Neuron_Structure_Get_Component(ns, i))) -> center[0]
  Graph_Workspace *gw = New_Graph_Workspace();

  Neuron_Structure_Weight_Graph(ns);
  Graph_To_Mst2_plus(ns->graph, gw);
  
  int i;
  int j = 0;
  for (i = 0; i < gw->nedge; i++) {
    if (gw->status[i] == 1) {
      Neurocomp_Conn_Copy(ns->conn + j, ns->conn + i);
      j++;
    }
  }

  Neuron_Structure_Unweight_Graph(ns);

  Kill_Graph_Workspace(gw);
}


void Graph_To_Mst2_plus(Graph *graph, Graph_Workspace *gw)
{
  if (GRAPH_EDGE_NUMBER(graph) == 0) {
    return;
  }

  TZ_ASSERT(Graph_Is_Weighted(graph), "The graph is not weighted.");

  Graph_Workspace_Prepare(gw, GRAPH_WORKSPACE_DEGREE);
  Graph_Workspace_Prepare(gw, GRAPH_WORKSPACE_VLIST);
  Graph_Workspace_Prepare(gw, GRAPH_WORKSPACE_ELIST);
  Graph_Workspace_Prepare(gw, GRAPH_WORKSPACE_STATUS);
  Graph_Workspace_Prepare(gw, GRAPH_WORKSPACE_DLIST);

  Graph_Workspace_Load(gw, graph);

  if (gw->degree == NULL) { /* store tree connection */
    gw->degree = iarray_malloc(gw->nvertex);
  }
  if (gw->vlist == NULL) { /* store tree identification */
    gw->vlist = iarray_malloc(gw->nvertex);
  }
  if (gw->elist == NULL) { /* store sorted edges */
    gw->elist = iarray_malloc(gw->nedge);
  }
  if (gw->dlist == NULL) {
    gw->dlist = darray_malloc(gw->nedge);
  }
  if (gw->status == NULL) { /* store added edges */
    gw->status = u8array_malloc(gw->nedge);
  }
  
  uint8_t *edge_in = gw->status;
  int *tree_id = gw->vlist;
  int *sorted_edge_idx = gw->elist;
  int *connection = gw->degree;
  double *weights = gw->dlist;
  
  int i;
  for (i = 0; i < graph->nedge; i++) {
    edge_in[i] = 0;
    sorted_edge_idx[i] = i;
  }
  for (i = 0; i < graph->nvertex; i++) // 并查集
  {
    tree_id[i] = i;
    connection[i] = -1;
  }

  darraycpy(weights, graph->weights, 0, gw->nedge);
  // 目测是朴素克鲁斯卡尔
  darray_qsort(weights, sorted_edge_idx, graph->nedge);

  int v1, v2;
  int tmpid;
  int next;
  for (i = 0; i < graph->nedge; i++) {
    QString s = QString::number(weights[sorted_edge_idx[i]]);
    std::string str_d = s.toStdString();
    // RECORD_INFORMATION("node");
    // RECORD_INFORMATION(str_d);

    v1 = graph->edges[sorted_edge_idx[i]][0];
    v2 = graph->edges[sorted_edge_idx[i]][1];

    // s = QString::number(v1);str_d = s.toStdString();RECORD_INFORMATION(str_d);
    // s = QString::number(v2);str_d = s.toStdString();RECORD_INFORMATION(str_d);

    if (tree_id[v1] != tree_id[v2]) {
      tmpid = tree_id[v2]; /* save id of v2 */
      /* change ids of v2-tree to v1*/
      next = tree_id[v2];
      while (next >= 0) {
        ASSERT(connection[next] != next, "self loop");
        tree_id[next] = tree_id[v1];
        next = connection[next];
      }				
      /******************************/

      /* connect v1-tree and v2-tree*/
      next = tree_id[v1];			
      while (connection[next] >= 0) {
        ASSERT(connection[next] != next, "self loop");
        next = connection[next];		
      }						
      connection[next] = tmpid;
      /******************************/

      edge_in[sorted_edge_idx[i]] = 1;
    }
  }

  int j = 0;
  for (i = 0; i < graph->nedge; i++) {
    if (edge_in[i] == 1) {
      graph->edges[j][0] = graph->edges[i][0];
      graph->edges[j][1] = graph->edges[i][1];
      graph->weights[j] = graph->weights[i];
      j++;
    }
  }
  
  graph->nedge = j;
}

